# titanium-ternjs

This small script generates [Tern](https://github.com/marijnh/tern) definition files from Appcelerator Titanium API documentation YAML files. Tern is code-analysis engine for JavaScript which adds intellisense capabilities to text editors, it uses definition files to autocomplete object model member names and infer their types.

## How to use

### Prerequisites

You should have tern already installed and text editor configured. Refer to [tern docs](http://ternjs.net/doc/manual.html#editor).

### Generating definition file

Clone titanium-ternjs repository:

    $ git clone git@github.com:x-cray/titanium-ternjs.git

Then you'll need Titanium Mobile source code which can be obtained from [titanium_mobile repository](https://github.com/appcelerator/titanium_mobile):

    $ git clone git@github.com:appcelerator/titanium_mobile.git

Optionally, you may want to checkout specific titanium_mobile release:

    $ cd titanium_mobile
    $ git checkout 3_1_2_GA
    $ cd ..

Run `generate.py` supplying path to source API documentation and output file:

	$ titanium-ternjs/generate.py titanium_mobile/apidoc titanium.json

Copy generated `titanium.json` file to your project directory. Then create `.tern-project` file in project directory (refer to [tern documentation](http://ternjs.net/doc/manual.html#configuration)) with the following contents:

```json
{
	"libs": [
		"titanium",
		"ecma5"
	],
	"plugins": {
		"requirejs": {
			"baseURL": "./app",
			"paths": {}
		}
	}
}
```

Libs entry `titanium` tells tern to look for `titanium.json` in project directory first and then in tern distribution `defs/` directory.

That's it. Now Titanium Mobile API autocomplete should work in your text editor.

## Contribution

Pull requests and ideas are welcome.
