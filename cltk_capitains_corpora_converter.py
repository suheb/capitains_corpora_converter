"""

"""
from glob import glob
import os
import git
import argparse
import logging
import json
import traceback


from MyCapytain.resources.inventory import TextGroup, TextInventory, Work, Citation
from MyCapytain.common.reference import URN
from MyCapytain.resources.texts.local import Text


logger = logging.getLogger("cltk_capitains_corpora_converter")


def toNumber(passages):
    """ Change the reference system of MyCapytain nested dict

    :param passages:
    :return:
    """
    returnDictionary = dict()
    passages_list = [passage for passage in passages.values()]
    for passage in passages_list:
        identifier = passages_list.index(passage)
        if isinstance(passage, dict):
            returnDictionary[identifier] = toNumber(passage)
        else:
            returnDictionary[identifier] = passage

    return returnDictionary


def make_json(text, textgroup, work, edition, exclude=None, credit="", commit=None):
    """ Make a json object out of a text and an inventory record

    :param text: Text object imported from CapiTainS standard
    :param text: MyCapytain.resources.texts.local.Text
    :param textgroup: Textgroup Metadata according to CapiTainS standards
    :type textgroup: MyCapytain.resources.inventory.Textgroup
    :param work: Work Metadata according to CapiTainS standards
    :type work: MyCapytain.resources.inventory.Work
    :param edition: Edition metadata according to CapiTainS standard
    :type edition: MyCapytain.resources.inventory.Edition or MyCapytain.resources.inventory.Translation
    :param exclude: Node to exclude such as tei:note
    :type exclude: list(str)
    :param credit: Line for Credit Attribution
    :type credit: str
    :param commit: Commit version
    :type commit: str
    :return: Json representation and filename
    """
    author = textgroup.metadata["groupname"]["eng"].lower()
    lang = [edition.lang or "unk"][0].lower()
    work = work.metadata["title"]["eng"].lower()

    j = {
        "original-urn": str(text.urn),
        "urn": "{}-simple".format(str(text.urn)),
        # Make a difference between both because losing TEI is changing the object
        "credit": credit,
        "meta": "-".join([citation.name or "unknown" for citation in text.citation]),
        "author": author.lower(),
        "work": work.lower(),
        "edition": edition.metadata["description"]["eng"],
        "text": toNumber(text.nested_dict(exclude=exclude))
    }
    if commit:
        j["commit"] = commit
    return json.dumps(j, ensure_ascii = False, indent=4, separators=(',', ':')), "{}__{}__{}.json".format(
        author,
        work,
        lang
    ).replace(" ", "_")


def parse_directory(directory):
    """ Parse a directory and yield required informations

    :param directory: Directory to parse
    :yields: Yields a tuple with the parsed texts and its parsed metadata
    :ytype: tuple(Text, Textgroup, Work, Edition)
    """
    textgroups = glob("{base_folder}/data/*/__cts__.xml".format(base_folder=directory))
    inventory = TextInventory()
    for __cts__ in textgroups:
        try:
            with open(__cts__) as __xml__:
                textgroup = TextGroup(resource=__xml__)
                textgroup.urn = URN(textgroup.xml.get("urn"))
            inventory.textgroups[str(textgroup.urn)] = textgroup

            for __subcts__ in glob("{parent}/*/__cts__.xml".format(parent=os.path.dirname(__cts__))):
                with open(__subcts__) as __xml__:
                    work = Work(
                        resource=__xml__,
                        parents=[inventory.textgroups[str(textgroup.urn)]]
                    )
                    work.urn = URN(work.xml.get("urn"))

                    inventory.textgroups[str(textgroup.urn)].works[str(work.urn)] = work

                for __text__ in inventory.textgroups[str(textgroup.urn)].works[str(work.urn)].texts.values():
                    __text__.path = "{directory}/{textgroup}.{work}.{version}.xml".format(
                        directory=os.path.dirname(__subcts__),
                        textgroup=__text__.urn.textgroup,
                        work=__text__.urn.work,
                        version=__text__.urn.version
                    )
                    if os.path.isfile(__text__.path):
                        try:
                            with open(__text__.path) as f:
                                t = Text(resource=f, urn=__text__.urn)
                                cites = list()
                                for cite in [c for c in t.citation][::-1]:
                                    if len(cites) >= 1:
                                        cites.append(Citation(
                                            xpath=cite.xpath.replace("'", '"'),
                                            scope=cite.scope.replace("'", '"'),
                                            name=cite.name,
                                            child=cites[-1]
                                        ))
                                    else:
                                        cites.append(Citation(
                                            xpath=cite.xpath.replace("'", '"'),
                                            scope=cite.scope.replace("'", '"'),
                                            name=cite.name
                                        ))
                            __text__.citation = cites[-1]
                            yield (
                                 t,
                                 inventory[str(textgroup.urn)],
                                 inventory[str(work.urn)],
                                 __text__
                            )
                        except Exception as E:
                            logger.error(
                                "%s does not accept parsing at some level (most probably citation) ",
                                __text__.path
                            )
                            logger.debug("Exact error message : %s", E.with_traceback(E.__traceback__))
        except Exception:
            logger.error("Error parsing %s ", __cts__)


def clone(repository, dest, branch=None, ref=None):
    """ Clone repository in dest folder

    :param repository: Repository to clone (eg. HTTPS addresses from GitHub)
    :param dest: Directory to clone to
    :param branch: Branch to pull (default: master)
    :param ref: Exact Reference to pull (default: refs/heads/master)
    :returns: Git Repository
    :rtype: git.repo

    """
    logger.info("Cloning %s into %s", repository, dest)
    repo = git.repo.base.Repo.clone_from(
        url=repository,
        to_path=dest
    )

    if ref is None:
        if branch is None:
            branch = "refs/heads/master"
            ref = branch
        else:
            ref = "refs/{0}".format(branch)

    repo.remote().pull(ref)
    logger.info("Cloning done.")

    return repo


def run(directory, output=None, repository=None, nodes=None, credit=None, silent=False):
    """ Run a full repository cloning

    :param directory: Directory in which to retrieve CapiTainS resources
    :param output: Output directory where we store the converted resources
    :param repository: GIT Repository to clone
    :param nodes: Nodes to remove from TEI using a list. eg. ["tei:note"]
    :param credit: Credit line to use in output json
    :param silent: Disable logging except for errors
    """
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if silent is True:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    if not output:
        output = "json-converted"

    if not os.path.exists(output):
        os.mkdir(output)

    if not credit:
        if repository:
            credit = "Downloaded from {}".format(repository)
        else:
            credit = ""

    if repository:
        repo = clone(repository, directory)
        last_commit = repo.head.commit.hexsha

    for text, textgroup, work, edition in parse_directory(directory):
        try:
            commit = None
            # If we cloned a repo, we try to get commit information. Right now, too consuming. Storing just last commit
            if repo:
                commit = last_commit

            _json, filename = make_json(text, textgroup, work, edition, nodes, credit=credit, commit=commit)
            filepath = os.path.join(output, *[filename])
            with open(filepath, "w") as f:
                logger.info("Writing %s", filepath)
                f.write(_json)
        except Exception as E:
            logger.error(
                "%s issued an error \n %s",
                edition.path,
                "\n".join([str(E)] + traceback.format_list(traceback.extract_tb(E.__traceback__)))
            )


def cmd():
    """ Commandline function to converter a CapiTainS Guidelines-based repository to a CLTK Corpus.
    """
    parser = argparse.ArgumentParser(description='CLTK Converter for CapiTainS based resources')
    parser.add_argument('directory', type=str,
                        help='List of path to use to populate the repository or destination directory for cloning')
    parser.add_argument('--output', type=str,
                        help='List of path to use to populate the repository or destination directory for cloning')
    parser.add_argument('--git', type=str, default=None, dest="repository",
                        help="Address of a repository")
    parser.add_argument('--credit', type=str, default=None,
                        help="Credit line to use in json")
    parser.add_argument('--exclude-nodes', type=str, nargs="+", default=None, dest="nodes",
                        help='Nodes to exclude from passages with "tei:" prefix, eg : --exclude-nodes tei:note tei:orig')
    parser.add_argument('--silent', action="store_true", default=False, dest="silent",
                        help='Show only errors')
    args = parser.parse_args()

    if args.directory:
        run(**vars(args))

if __name__ == "__main__":
    cmd()
