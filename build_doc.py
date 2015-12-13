#!/usr/bin/python

import os
import sys
import yaml
import shutil
import argparse
from subprocess import call
from os.path import isfile, join

def parse_args():
	parser = argparse.ArgumentParser(description='Compile markdown documentation files into HTML or PDF')
	parser.add_argument('source_dir', metavar='source', help='Source path of the documentation')
	parser.add_argument('-b', '--build_all', help='Build all version from git', action='store_true')
	return parser.parse_args()

def yaml_load(filename):
	stream = file(filename, 'r')
	obj = yaml.load(stream)
	stream.close()
	return obj

def write_to_file(content, filepath):
	text_file = open(filepath, "w")
	text_file.write(content)
	text_file.close()

def read_file(filepath):
	text_file = open(filepath, "r")
	content = text_file.read()
	text_file.close()
	return content

def remove_file(filename):
	if os.path.exists(filename):
		os.remove(filename)

def get_template(filename):
	return read_file(theme_dir + "/" + filename)
		
def gen_meta_files(doc_meta, cur_version, versions, meta_dir):
	# Generate the title file
	title = get_template('template_title.html') % doc_meta['title']
	write_to_file(title, meta_dir + "/header_title.html")
	
	prefix = doc_meta['file_prefix']
	version_item_template = get_template('template_version_item.html')
	version_items = []
	for version in versions:
		version_items.append(version_item_template % (prefix, version, version))
	
	template_version = get_template('template_version.html') % (cur_version, '\n'.join(version_items))
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
	md_files.sort()
	for md_file in md_files:
		md_file_path = md_dir + "/" + md_file
		pandoc_args.append(md_file_path)

	call(pandoc_args)

def gen_doc_file(version):
	gen_meta_files(doc_meta, version, versions, meta_dir)
	file_prefix = doc_meta['file_prefix']
	filename = "%s%s.html" % (file_prefix, version)
	target_file = "%s/%s" % (html_dir, filename)
	compile_pandoc(source_dir, theme_dir, meta_dir, target_file)
	return filename


def git_checkout(git_path, branch):
	print
	print "#### Checking out Git Branch:", branch
	cmd_prefix = './'
	if os.name == 'nt':
		cmd_prefix = ''
	shell_args = [cmd_prefix + 'git_checkout.sh', git_path, branch]
	print shell_args
	call(shell_args, shell=True);

def create_index_file(redirect_filename):
	redirect_path = "html/" + redirect_filename
	if args.build_all:
		redirect_path = "stage/" + redirect_path

	redirect_html = read_file(theme_dir + "/index_redirector.html")
	redirect_html = redirect_html % (redirect_path, redirect_path)
	# Save this in the gen folder as index.html
	write_to_file(redirect_html, gen_dir + "/index.html")


# Parse commandline args
args = parse_args()
source_dir = args.source_dir

# Load the meta data from the source directory
if args.build_all:
	git_checkout(source_dir, 'gh-pages')
	doc_meta = yaml_load(source_dir + "/doc.yaml")
	gen_meta = yaml_load(source_dir + "/generator.yaml")
	versions = yaml_load(source_dir + "/versions.yaml")
else:
	doc_meta = {'file_prefix': 'doc_', 'title': 'Documentation'}
	gen_meta = {'pdf': False, 'theme': 'skyblue'}
	versions = ['0']
config = yaml_load("./config.yaml")
	
# Recreate the output dir
gen_dir = config['temp_stage_dir']
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

latest_version_filename = None
for version in versions:
	if args.build_all:
		git_checkout(source_dir, version)

	doc_filename = gen_doc_file(version)
	if latest_version_filename is None:
		latest_version_filename = doc_filename

	if not args.build_all:
		break

create_index_file(latest_version_filename)


# Remove the intermediate folder
shutil.rmtree(meta_dir, True)

# If we built for all version, then place the stage directory in the gh-pages branch
if args.build_all:
	git_checkout(source_dir, 'gh-pages')
	source_stage = source_dir + "/stage"
	shutil.rmtree(source_stage, True)
	shutil.copytree(gen_dir, source_stage)
	remove_file(source_dir + "/index.html")
	shutil.move(source_stage + "/index.html", source_dir)



