# Markdown Code Packer

## Motivation

I often want to save code files in my markdown notes, but they disrupt the reading flow.
Sometimes I just want to include them if I ever want to reproduce the spike project.
Sometimes I create gist.

Examples:
- webpack / rollup spike
- My setup (which includes config files) settings
- Insert an image?

- see [[202003292017]])
- record GIFs

Goal: archive a whole project in a single file (only source code). For explanations and notes)

Example: unfolded incomplete code, below the full file

## Sublime Plugin

- How does it work?

- Unpack
- Pack
- Extract single to folder (can include relative path)
- Extract all to folder (can include relative path)
- Pack folder
- select multiple lines/code blocks to pack/unpack them at same time

## Installation

- With Package Control: Open the command palette and run the `Package Control: Install Package` command, find and install the `Markdown Code Packer` plugin.
- Manually: Clone or download git repository into your packages folder (to find the folder run the command `Preferences - Browse Packages`).

## Demo Documents

- [Test](demos/Test.md): Use for playing around
- [My Mac Setup](demos/My Mac Setup.md): Includes packed config files.
- [Webpack](demos/Webpack.md): Includes mini-projects, make sure to select one and then extract it to a folder

_If you are wondering what `[[202003271748]]` means: These are references to other notes (see [Sublime ZK](https://github.com/renerocksai/sublime_zk) for more info)._

## Choices

- why use comments?
- why use deflate and base64?

## Contribute

...

- To generate a new sublime package (for submission to `packagecontrol.io`) use the command `Package Control: Create Package File`.

Contact me via ...

## TODO

- write README
- Support binaries and other encodings than UTF-8
- Rename to Markdown Code Archive?
- Add versioning: If you are using GitHub or BitBucket for your hosting, you will need to create a tag each time you want to make a new version available to users. The tag names must be a semantic version number. 
- Publish
  - Package Control: https://packagecontrol.io/docs/submitting_a_package#Step_6
  - HackerNews
- Command line tool? & Brew formula
- remember/infer file type for fenced code blocks
- export all files in this file to a directory (similar to "Move...")
