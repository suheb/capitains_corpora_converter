# Capitains Corpora Converter

Converts CapiTainS-based Repository ( http://capitains.github.io ) to JSON for CLTK

## How to install ?

### Install as a package
    
```shell
git clone https://github.com/cltk/capitains_corpora_converter.git
cd capitains_corpora_converter
pyvenv venv
source venv/bin/activate
python setup install
```

### Install for development

```shell
git clone https://github.com/cltk/capitains_corpora_converter.git
cd capitains_corpora_converter
pyvenv venv
source venv/bin/activate
python setup develop
```

### Install as global commandline

**Not recommanded**

```shell
git clone https://github.com/cltk/capitains_corpora_converter.git
cd capitains_corpora_converter
sudo python setup install
```

## Command Line Interface

capitains-cltk-converter [-h] [--output OUTPUT] [--git REPOSITORY]
                                [--credit CREDIT]
                                [--exclude-nodes NODES [NODES ...]] [--silent]
                                directory

CLTK Converter for CapiTainS based reosurces

**Positional arguments:**

| Argument name                     | Description                                                                              |
|----------------------------------:|------------------------------------------------------------------------------------------|
| directory                         | List of path to use to populate the repository or destination directory for cloning      |

**Optional Arguments:**

| Argument name                     | Description                                                                              |
|----------------------------------:|------------------------------------------------------------------------------------------|
| -h, --help                        | Show this help message and exit                                                          |
| --output OUTPUT                   | List of path to use to populate the repository or destination directory for cloning      |
| --git REPOSITORY                  | Address of a repository                                                                  |
| --credit CREDIT                   | Credit line to use in json                                                               |
| --exclude-nodes NODES [NODES ...] | Nodes to exclude from passages with "tei:" prefix, eg: --exclude-nodes tei:note tei:orig |
| --silent                          | Show only errors                                                                         |


## Example

### Converting Open Greek And Latin's CSEL 

With the virtual env activated or with global commandline :

```shell
capitains-cltk-converter cloning --git https://github.com/OpenGreekAndLatin/csel-dev.git --credit "Open Philology, Humboldt Chair of Digital Humanities ( https://github.com/OpenGreekAndLatin/csel-dev )" --exclude-nodes tei:note tei:orig
```
