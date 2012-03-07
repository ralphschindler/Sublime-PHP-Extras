PHP_BIN = "php"

import sublime, sublime_plugin

import os
import subprocess
import tempfile

class PhpRunCodeCommand (sublime_plugin.TextCommand):

    def run (self, edit):
        expression = ""

        # first attempt to fill expression from concatenation
        # of selection regions.
        for sel in self.view.sel():
            expression += self.view.substr(sel) + "\n"

        expression = expression.strip()

        # if this is a segment, assume it needs to be wrapped in <?php
        # change this later to pass the -r to the php binary
        if expression:
            expression = "<?php\n%s" % (expression)
        else:
            expression = self.view.substr(sublime.Region(self.view.size(), 0))

        # if there is still nothing, return now.
        if not expression:
            return

        # create a temporary file to house expression.
        fh, fname = tempfile.mkstemp()
        os.write(fh, expression)
        os.close(fh)

        content = "PHP OUTPUT\n=========="

        # execute expression through PHP and capture stdout/stderr.
        process  = subprocess.Popen([PHP_BIN, fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()

        # erase temporary file.
        os.unlink(fname)

        # write stdout and any stderr to new panel.
        view = self.view.window().new_file()
        edit = view.begin_edit()

        content = "%s\n\n%s" % (content, out)

        if err:
            out = "%s\n\nERROR:\n%s" % (out, err)

        view.insert(edit, 0, content)
        view.end_edit(edit)