#!/usr/bin/python

import os
import sys
import yaml
import shutil
from subprocess import call
from os.path import isfile, join

def check_args():
	if (len(sys.argv) != 3):
		print """\
		Usage: build_doc <source_dir> <target_dir>
		"""
		sys.exit(1)

def yaml_load(filename):
	stream = file(filename, 'r')
	obj = yaml.load(stream)
	stream.close()
	return obj

def write_to_file(content, filepath):
	text_file = open(filepath, "w")
	text_file.write(content)
	text_file.close()

def gen_meta_files(doc_meta, cur_version, versions, meta_dir):
	title = """
			<div class="doc-title">%s</div>
	""" % doc_meta['title']
	write_to_file(title, meta_dir + "/header_title.html")

	prefix = doc_meta['file_prefix']
	version_item_template = "<li><a href=\"%s%s.html\">%s</a></li>"
	version_items = []
	for version in versions:
		version_items.append(version_item_template % (prefix, version, version))

	template_version = """
			<div class="version-number">[%s]</div><div id="version-block" style="display: inline">
			  <div class="dropdown">
			    <button class="btn btn-primary dropdown-toggle" type="button" data-toggle="dropdown">Version
			    <span class="caret"></span></button>
			    <ul class="dropdown-menu">
			    %s
			    </ul>
			  </div>
			</div>
	""" % (cur_version, '\n'.join(version_items))
	write_to_file(template_version, meta_dir + "/header_versions.html")





def compile_pandoc(source_dir, theme_dir, meta_dir, target_file):
	# Get the list of all the source markdown files
	pandoc_args = [
		'pandoc', '-s', '-S', '--toc',
		'-o', target_file,
		'-H', theme_dir + "/include.html",
		'-B', theme_dir + "/header_main.html",
		'-B', meta_dir + "/header_versions.html",
		'-B', meta_dir + "/header_title.html",
		'-A', theme_dir + "/footer.html",
	]

	md_dir = source_dir + "/source"
	md_files = [f for f in os.listdir(md_dir) if isfile(join(md_dir, f))]
	for md_file in md_files:
		md_file_path = md_dir + "/" + md_file
		pandoc_args.append(md_file_path)

	call(pandoc_args)


check_args()

source_dir = sys.argv[1]
target_dir = sys.argv[2]

# Load the meta data from the source directory
doc_meta = yaml_load(source_dir + "/doc.yaml")
gen_meta = yaml_load(source_dir + "/generator.yaml")
versions = yaml_load(source_dir + "/versions.yaml")

# Recreate the output dir
gen_dir = "/tmp/stage"
html_dir = gen_dir + "/html"
shutil.rmtree(gen_dir, True)
os.makedirs(gen_dir)
os.makedirs(html_dir)

#Copy the theme
theme_name = gen_meta["theme"]
theme_dir = "themes/" + theme_name
shutil.copytree(theme_dir + "/theme", gen_dir + "/theme");

# Copy the documentation assets
shutil.copytree(source_dir + "/assets", gen_dir + "/assets");

# Generate document specific dynamic files
meta_dir = gen_dir + "/tmp"
os.makedirs(meta_dir)

file_prefix = doc_meta['file_prefix']
for version in versions:
	gen_meta_files(doc_meta, version, versions, meta_dir)
	target_file = html_dir + "/%s%s.html" % (file_prefix, version)
	compile_pandoc(source_dir, theme_dir, meta_dir, target_file)

shutil.rmtree(meta_dir, True)

