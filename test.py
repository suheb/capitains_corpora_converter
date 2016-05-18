from cltk_capitains_corpora_converter import make_json, toNumber, parse_directory, cmd, clone
from collections import OrderedDict
from unittest import TestCase
import json

from MyCapytain.resources.inventory import TextInventory
from MyCapytain.common.reference import URN
from MyCapytain.resources.texts.local import Text


def get_test_resources():
    """ Create a set of test resources

    :return: dict with keywords for make_json
    """
    with open("test_data/repo/data/textgroup/work/textgroup.work.version-lat1.xml") as file:
        text = Text(resource=file, urn="urn:cts:latinLit:textgroup.work.version-lat1")

    with open("test_data/repo/full_inventory.xml") as file:
        inventory = TextInventory(resource=file)
    work = inventory["urn:cts:latinLit:textgroup.work"]
    textgroup = inventory["urn:cts:latinLit:textgroup"]
    edition = inventory["urn:cts:latinLit:textgroup.work.version-lat1"]

    return {
        "text": text,
        "work": work,
        "textgroup": textgroup,
        "edition": edition
    }


class TestFunctions(TestCase):
    """ Test individual functions and not the whole process
    """
    def test_toDic(self):
        """ Ensure toDic function creates nested dict with int as keys from ordered dict with string keys
        """
        test_dict = OrderedDict([
            ("a", OrderedDict([
                ("1", "Some text"),
                ("2", "Some other Text")
            ])),
            ("b", OrderedDict([
                ("7", "Lorem"),
                ("e", "Ipsum")
            ]))
        ])
        a = toNumber(test_dict)
        expected = {
            0: {
                0: "Some text",
                1: "Some other Text"
            },
            1: {
                0: "Lorem",
                1: "Ipsum"
            }
        }
        self.assertEqual(a, expected, "Nested should be converted to nested dictionary with int indexes")

    def test_make_json_simple(self):
        """ Test make json with default values
        """
        resources = get_test_resources()
        output, filename = make_json(**resources)
        output = json.loads(output)
        self.assertEqual(
            output["text"]["0"]["0"]["0"], "Spero me secutum in libellis meis tale temperamen-",
            "Text passages should be parsed correctly"
        )
        self.assertEqual(
            output["text"]["1"]["0"]["0"], "Qui tecum cupis esse meos ubicumque libellos ",
            "Text passages should be parsed correctly"
        )

        self.assertEqual(
            output["text"]["1"]["0"]["1"], "Et comites longae quaeris habere viae, Something",
            "Text passages should be parsed correctly and note kept"
        )
        self.assertEqual(
            output["text"]["1"]["1"]["3"], "Crede slug. mihi, nimium Martia turba sapit. ",
            "Text passages should be parsed correctly and abbr kept"
        )
        self.assertEqual(
            filename, "textgroup__work__lat.json",
            "Filename should be created in a stable and understandable manner"
        )
        self.assertEqual(
            output["original-urn"], "urn:cts:latinLit:textgroup.work.version-lat1",
            "Original URN should be fed"
        )
        self.assertEqual(
            output["urn"], "urn:cts:latinLit:textgroup.work.version-lat1-simple",
            "CLTK URN should be suffixed"
        )
        self.assertEqual(
            output["credit"], "",
            "Credit should be empty by default"
        )
        self.assertEqual(
            output["meta"], "book-poem-line",
            "meta should reflect the citation scheme"
        )
        self.assertEqual(
            output["author"], "textgroup",
            "Author name should be the English textgroup name"
        )
        self.assertEqual(
            output["work"], "work",
            "Work name should be the English work name"
        )
        self.assertEqual(
            output["edition"], "description",
            "We should have the  English description"
        )

    def test_make_json_advanced(self):
        """ Test make json with default values
        """
        resources = get_test_resources()
        output, filename = make_json(commit="1245", exclude=["tei:note", "tei:orig"], credit="PerseusDL", **resources)
        output = json.loads(output)
        self.assertEqual(
            output["text"]["0"]["0"]["0"], "Spero me secutum in libellis meis tale temperamen-",
            "Text passages should be parsed correctly"
        )
        self.assertEqual(
            output["text"]["1"]["0"]["1"], "Et comites longae quaeris habere viae, ",
            "Text passages should be parsed correctly and note removed"
        )
        self.assertEqual(
            output["text"]["1"]["1"]["3"], "Crede mihi, nimium Martia turba sapit. ",
            "Text passages should be parsed correctly and note removed"
        )
        self.assertEqual(
            output["text"]["1"]["0"]["0"], "Qui tecum cupis esse meos ubicumque libellos ",
            "Text passages should be parsed correctly"
        )
        self.assertEqual(
            filename, "textgroup__work__lat.json",
            "Filename should be created in a stable and understandable manner"
        )
        self.assertEqual(
            output["original-urn"], "urn:cts:latinLit:textgroup.work.version-lat1",
            "Original URN should be fed"
        )
        self.assertEqual(
            output["urn"], "urn:cts:latinLit:textgroup.work.version-lat1-simple",
            "CLTK URN should be suffixed"
        )
        self.assertEqual(
            output["credit"], "PerseusDL",
            "Credit should be empty by default"
        )
        self.assertEqual(
            output["meta"], "book-poem-line",
            "meta should reflect the citation scheme"
        )
        self.assertEqual(
            output["author"], "textgroup",
            "Author name should be the English textgroup name"
        )
        self.assertEqual(
            output["work"], "work",
            "Work name should be the English work name"
        )
        self.assertEqual(
            output["edition"], "description",
            "We should have the  English description"
        )
        self.assertEqual(
            output["commit"], "1245",
            "We should have the commit information"
        )

    def test_parse_directory(self):
        """ Ensure parse directory works
        """
        parsed = [i for i in parse_directory("./test_data/repo")]
        self.assertEqual(
            len(parsed), 2,
            "There should be two texts which are found"
        )

    def test_parse_directory_and_make_json(self):
        """ Test that we can reuse this for makejson
        """
        parsed = [i for i in parse_directory("./test_data/repo")]
        json_obj, filename = make_json(*parsed[0])
        json_parsed = json.loads(json_obj)
        self.assertEqual(
            json_parsed["text"]["0"]["0"]["0"], "Spero me secutum in libellis meis tale temperamen-",
            "Text passages should be parsed correctly"
        )
        self.assertEqual(
            filename, "textgroup__work__lat.json",
            "Filename should be created in a stable and understandable manner"
        )

        json_obj, filename = make_json(*parsed[1])
        json_parsed = json.loads(json_obj)
        self.assertIn(
            "cit, nobis magno consensu vitia", json_parsed["text"]["0"]["0"],
            "Text passages should be parsed correctly"
        )
        self.assertEqual(
            filename, "groupe_de_texte__oeuvre__lat.json",
            "Filename should be created in a stable and understandable manner"
        )


class TestCommand(TestCase):
    def test_something(self):
        pass