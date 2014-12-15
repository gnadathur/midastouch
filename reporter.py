import os

import jinja2 as jj2


class HTMLReporter(object):
    def __init__(self):
        self.fpath = os.path.dirname(os.path.realpath(__file__))
        self.loader = jj2.FileSystemLoader(self.fpath)
        self.env = jj2.Environment(loader=self.loader,
                                   extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols", ])

    def addContent(self, cntnt, c_id, title):
        r = {}
        r['title'] = title
        r['id'] = c_id
        r['content'] = cntnt
        template = self.env.get_template(self.block_templ)
        rep = template.render(cntnt=r)
        self.report_content.append(rep)
        return

    def renderReport(self):
        template = self.env.get_template(self.report_templ)
        out = template.render(dbg=self.dbg, all_content=self.report_content,
                              chart_tables=self.ch_obj.all_charts)
        f = open(self.dest_file, 'w')
        f.write(out)
        f.close()
        print "Written ", self.dest_url
        