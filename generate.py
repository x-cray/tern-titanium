#!/usr/bin/python

import sys
import os
import re
import yaml
import json

known_types = ['Number', 'String']

def get_js_type(type):
	if isinstance(type, basestring):
		if type in known_types:
			return type.lower()
		if type == 'Boolean':
			return 'bool'
		array_match = re.match(r'Array<(\w+)>', type)
		if array_match:
			sub_type = array_match.group(1)
			js_type = get_js_type(sub_type)
			if js_type:
				return '[%s]' % js_type
	if isinstance(type, list) and len(type) > 0:
		return get_js_type(type[0])

def get_fn_type(method_dict):
	params = ''
	if method_dict.has_key('parameters'):
		params = ', '.join(['%s: %s' % (param['name'], get_js_type(param['type'])) for param in method_dict['parameters']])
	ret = ''
	if method_dict.has_key('returns'):
		returns_dict = method_dict['returns']
		return_js_type = isinstance(returns_dict, dict) and get_js_type(returns_dict['type']) or None
		if return_js_type:
			ret = ' -> %s' % return_js_type
	return 'fn(%s)%s' % (params, ret)

def fill_properties(properties, dict):
	for property in properties:
		prop_descriptor = {}
		if property.has_key('summary'):
			prop_descriptor['!doc'] = property['summary']
		prop_type = get_js_type(property['type'])
		if prop_type:
			prop_descriptor['!type'] = prop_type
		dict[property['name']] = prop_descriptor

def fill_methods(methods, dict):
	for method in methods:
		method_descriptor = {}
		if method.has_key('summary'):
			method_descriptor['!doc'] = method['summary']
		fn_type = get_fn_type(method)
		if fn_type:
			method_descriptor['!type'] = fn_type
		dict[method['name']] = method_descriptor

def parse_yaml_doc(doc):
	curr_dict = result
	sections = doc['name'].split('.')
	last_section = None

	# Generate objects hierarchy.
	for section in sections:
		last_section = section
		if section == 'Global':
			continue
		if not curr_dict.has_key(section):
			new_dict = {}
			curr_dict[section] = new_dict
			curr_dict = new_dict
		else:
			curr_dict = curr_dict[section]

	# Generate summary, properties and methods documentation.
	curr_dict['!doc'] = doc['summary']

	prototype_dict = None
	if not doc.has_key('extends') or doc['extends'] == 'Titanium.Module':
		prototype_dict = curr_dict
	else:
		prototype_dict = {}
		curr_dict['prototype'] = prototype_dict
		curr_dict['!proto'] = doc['extends']

	if doc.has_key('properties'):
		fill_properties(doc['properties'], prototype_dict)

	if doc.has_key('methods'):
		fill_methods(doc['methods'], prototype_dict)

	if not doc.has_key('createable') or doc['createable'] == 'true':
		return {
			'name': 'create%s' % last_section,
			'returns': {
				'type': last_section
			}
		}

def read_yaml_file(file):
	print 'Reading %s' % file
	create_methods = []
	f = open(file)
	docs = yaml.load_all(f)
	for doc in docs:
		create_method = parse_yaml_doc(doc)
		if create_method:
			create_methods.append(create_method)
	f.close()
	return create_methods

# Check console args.
if len(sys.argv) < 3:
	print 'Usage: %s <yaml_dir> <output_file>' % sys.argv[0]
	exit(1)

yaml_dir = sys.argv[1]
output_file = sys.argv[2]
global_create_methods = []
result = {
	# Module name.
	'name': 'titanium',
	
	# Make a global Ti alias to Titanium.
	'Ti': {
		'!proto': 'Titanium'
	}
}

# Enumerate all files in yaml_dir.
for root, dir, files in os.walk(yaml_dir):
	for file in files:
		if file.endswith('.yml'):
			file_create_methods = read_yaml_file(os.path.join(root, file))
			if len(file_create_methods):
				global_create_methods.extend(file_create_methods)

fill_methods(global_create_methods, result['Titanium']['UI'])

print 'Writing result to %s' % output_file
f = open(output_file, 'w')
f.write(json.dumps(result, indent=4, separators=(',', ': ')))
f.close()
