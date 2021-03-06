#!/usr/bin/env python
# coding: utf-8

import semanticscholar as sch
import networkx as nx
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool, Plot, Range1d, ResetTool, PanTool, MultiLine)
from bokeh.layouts import row
from bokeh.plotting import from_networkx
from bokeh.colors import RGB
import itertools
import time
import pandas as pd

class Citree(object):
    """
    a class that creates a citation tree.
    the input is the doi of the paper you want to start with.
    parameters: DOI of a paper (foe example, 10.1002/ejp.1639).
    the data is retrieved using semanticscholar package
    (API that works with https://www.semanticscholar.org/).
    the network is built by using Networkx package.
    the plotting is done by using Bokeh package.

    attributes:
    --------------
        first_doi - the doi provided by the user
        n_gen - number of generations of citations. by default=2
        filename - for creating HTML and CSV files
        paper - a semanticscholar class (api that works with https://www.semanticscholar.org/)
        plot_name - plot title based on the name and author of the paper provided
        G - networkx object of the papers network
        A - networkx object of the authors plot
        generation - stores the number of generations
            (iterations of create_next_generation method)

    methods:
    --------------
    first - creates the first node
    create_next_generation - creates nodes based on papaers that cited
        the last generation nodes.
        saves a backup gpickle file.
        prints the generaton nuber and how many papers were found.
    color_by_self_citation - needs an input of authorId.
        colors in red nodes of papers which the input author is a co-author.
        the other nodes and edges are green.
        the authors names are stored at paper['authors']
    plot_html(filename='filename) - creats an html file with tow plots:
        1. on the left: papers cictations tree
        2. on the right: authors who wrote toghather
    export_csv(filename='filename) - saves a csv file

    """
    def __init__(self, first_doi, n_gen=2, filename='filename'):
        self.first_doi = first_doi
        self.n_gen = n_gen
        self.paper = sch.paper(first_doi)  # semantic scholar api
        self.plot_name = self.paper['title']
        self.filename = filename
        self.done_dois = []
        self.redo_dois = []
        self.G = nx.MultiGraph()  # article titles graph
        self.A = nx.MultiGraph()  # authors graph
        self.generation = 0
        self.retrived_count = 0  # semantic scholar limits 100 retrievals per 5 min. sleep for 5 min when counter=99
        self.first_authors_ids = []
        self.max_degree = 0
        self.df = pd.DataFrame()

        self.first()
        for i in range(n_gen):
            self.create_next_generation()
        self.color_by_self_citation()
        self.plot_html(filename=filename)
        self.export_csv(filename=filename)

    def first(self):
        """
        creates the first node and attributes for:
            1. G - papers' titles graph
            2. A - authors grap
        """
        f_title_ = self.paper['title']
        f_doi_ = self.first_doi
        f_journal_ = self.paper['venue']
        f_year_ = self.paper['year']
        f_abstract = self.paper['abstract']
        f_authors_ = []
        f_authorIds_ = []
        # create a list of authors
        for auth in self.paper['authors']:
            f_authors_.append(auth['name'])
            f_authorIds_.append(auth['authorId'])
            self.first_authors_ids.append(auth['authorId'])
            # add nodes for authors graph with names of all the authors, based on author id
            self.A.add_node(auth['authorId'])
            # add name attribute to author node
            self.A.nodes[auth['authorId']]['name'] = auth['name']
            # add author id attribute to author node
            self.A.nodes[auth['authorId']]['authorId'] = auth['authorId']

        # edges links between all authors of the paper (for aouthors plot)
        # chekc if there's more than 1 author
        if len(list(self.A)) > 1:
            # create author list
            node_list = [node for node in list(self.A)]
            # create list of combinations so all authors will be conected onr to another
            all_combinations = list(itertools.combinations(node_list, 2))
            # create all author nodes
            for comb in all_combinations:
                self.A.add_edge(comb[0], comb[1])

        f_citations_dois_ = []
        # iterate over papers that cited the first paper for next generation
        if len(self.paper['citations']) > 0:  # check if paper was cited
            for dic in self.paper['citations']:
                if dic['doi'] is not None:
                    f_citations_dois_.append(dic['doi'])
        # add node and set attributes
        self.G.add_node(f_doi_)
        self.G.nodes[f_doi_]['title'] = f_title_
        self.G.nodes[f_doi_]['doi'] = self.first_doi
        self.G.nodes[f_doi_]['journal'] = f_journal_
        self.G.nodes[f_doi_]['year'] = f_year_
        self.G.nodes[f_doi_]['authors'] = f_authors_
        self.G.nodes[f_doi_]['citations_dois'] = f_citations_dois_
        self.G.nodes[f_doi_]['abstract'] = f_abstract
        # add author id attribute to author node
        self.G.nodes[f_doi_]['authorIds'] = f_authorIds_
        # self.G.nodes[f_doi_]['citations_titles'] = f_citations_titles_
        self.G.nodes[f_doi_]['size'] = 6
        self.done_dois.append(self.first_doi)
        self.retrived_count += 1

    def create_next_generation(self):

        if self.generation == 0:
            node_list = [node for node in list(self.G)]
            self.done_dois.append(self.first_doi)
        else:
            node_list = [node for node in list(self.G) if ((node not in self.done_dois) and len(node) > 1)]  # len(node)>1 to avoid )
            self.done_dois += node_list + self.redo_dois
        for node in node_list:
            for doi_ in self.G.nodes[node]['citations_dois']:
                if self.retrived_count > 99:
                    time.sleep(300)
                    self.retrived_count = 0
                try:
                    paper = sch.paper(doi_, timeout=350)
                except KeyError:
                    pass
                try:
                    title_ = paper['title']
                except KeyError:
                    title_ = 'none'
                try:
                    journal_ = paper['venue']
                except KeyError:
                    journal_ = 'none'
                try:
                    abstract_ = paper['abstract']
                except KeyError:
                    abstract_ = 'none'
                try:
                    year_ = paper['year']
                except KeyError:
                    year_ = 'none'
                try:
                    authors_ = []
                    author_ids = []
                    for auth in paper['authors']:
                        authors_.append(auth['name'])
                        author_ids.append(auth['authorId'])
                        # remove None
                        authors_ = list(filter(None, authors_))
                        author_ids = list(filter(None, author_ids))
                    all_combinations = list(itertools.combinations(author_ids, 2))
                    # create all author nodes in authors' graph
                    for comb in all_combinations:
                        self.A.add_edge(comb[0], comb[1])
                    for auth in paper['authors']:
                        # add name attribute to nodes
                        self.A.nodes[auth['authorId']]['name'] = auth['name']
                        # add authorId attribute
                        self.A.nodes[auth['authorId']]['authorId'] = auth['authorId']
                except KeyError:
                    authors_ = 'none'
                    author_ids = []
                citations_dois_ = []

                try:
                    if len(paper['citations']) > 0:  # check paper was cited
                        for dic in paper['citations']:
                            if dic['doi'] is not None and len(dic['doi']):
                                citations_dois_.append(dic['doi'])
                        citations_dois_ = list(filter(None, citations_dois_))  # remove None
                        if len(citations_dois_) > self.max_degree:
                            self.max_degree = len(citations_dois_)
                except KeyError:
                    pass

                self.G.add_edge(node, doi_)
                self.G.nodes[doi_]['title'] = title_
                self.G.nodes[doi_]['doi'] = doi_
                self.G.nodes[doi_]['journal'] = journal_
                self.G.nodes[doi_]['year'] = year_
                self.G.nodes[doi_]['authors'] = authors_
                self.G.nodes[doi_]['citations_dois'] = citations_dois_
                self.G.nodes[doi_]['abstract'] = abstract_
                self.G.nodes[doi_]['authorIds'] = author_ids
                self.G.nodes[doi_]['size'] = 2.5
                if title_ == 'none' and journal_ == 'none' and year_ == 'none':
                    self.redo_dois.append(doi_)
                self.retrived_count += 1
        # save temporary file
        nx.write_gpickle(self.G, 'temp_generation_'+str(self.generation)+'.gpickle')
        self.generation += 1
        print('generation:', self.generation)
        print(len(list(self.G)), 'papers were found in the next generation')

    def color_by_self_citation(self):
        """
        if the citing article was written by the same authors
        as the original paper (self.first_authors_ids), color the node in red.
        """
        # define colors
        red = RGB(r=255, g=0, b=0)
        green = RGB(r=0, g=255, b=0)

        # red color for the self.first_authors_ids nodes in the authors graph
        for node in list(self.A):
            try:
                self.A.nodes[node]['color'] = red if self.A.nodes[node]['authorId'] in self.first_authors_ids else green
            except KeyError:
                self.A.nodes[node]['color'] = green

        # color first node red
        self.G.nodes[self.first_doi]['color'] = red
        # color red nodes if the base autor also wrote the citing article
        for node in list(self.G):
            neighbors = self.G.neighbors(node)
            for neighbor in neighbors:
                if any(x in self.first_authors_ids for x in self.G.nodes[neighbor]['authorIds']):
                    self.G.nodes[neighbor]['color'] = red
                else:
                    self.G.nodes[neighbor]['color'] = green

        # color the edges connecting the nodes with same authorIds as in the first paper
        for start_node, end_node, _ in self.G.edges(data=True):
            condition = (any(x in self.first_authors_ids for x in self.G.nodes[end_node]["authorIds"])) and (
                any(x in self.first_authors_ids for x in self.G.nodes[start_node]["authorIds"]))

            self.G.adj[start_node][end_node][0]['edge_color'] = red if condition else green

    def plot_html(self, filename="filename"):
        """
        plotting the network using Bokeh package.
        plot1 is the article titles graph. based on doi
        plot2 is the authors graph. based on author id
        the input is the filename without extension
        """
#       iterate over nodes,convert lists to string to avoid error and create "size" attribute
        for node in list(self.G):
            for key in self.G.nodes[node].keys():
                if isinstance(self.G.nodes[node][key], list):
                    self.G.nodes[node][key] = ' '.join([str(elem) for elem in self.G.nodes[node][key]])
        # Show with Bokeh
        plot1 = Plot(x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
        plot1.title.text = self.plot_name
        graph_renderer = from_networkx(self.G, nx.spring_layout, scale=0.1, center=(0, 0))
        graph_renderer.node_renderer.glyph = Circle(size=5, fill_color='color')
        graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color", line_alpha=0.8, line_width=1)

        tooltips = [("title", "@title"), ("author", "@authors"),
                    ("year", "@year"), ("journal", "@journal"), ("doi", "@doi")]
        node_hover_tool = HoverTool(tooltips=tooltips)
        plot1.add_tools(node_hover_tool, BoxZoomTool(), ResetTool(), PanTool(),)
        plot1.renderers.append(graph_renderer)

        plot2 = Plot(x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
        plot2.title.text = 'authors'
        graph2_renderer = from_networkx(self.A, nx.spring_layout, scale=0.1, center=(0, 0))
        graph2_renderer.node_renderer.glyph = Circle(size=5, fill_color='color')
        tooltips2 = [("name", "@name"), ("author id", "@authorId"), ]
        node_hover_tool2 = HoverTool(tooltips=tooltips2)
        plot2.add_tools(node_hover_tool2, BoxZoomTool(), ResetTool(), PanTool())
        plot2.renderers.append(graph2_renderer)

        output_file(filename+'.html', mode='cdn')
        show(row(plot1, plot2))

    def export_csv(self, filename='filename'):
        """
        creates a dataframe and exports it as 'filename.csv'
        """
        cols = ['doi', 'title', 'journal', 'year', 'authors', 'citations_dois', 'abstract']
        row_list = []
        for node in self.G.nodes():
            row = [self.G.nodes[node]['doi'],
                   self.G.nodes[node]['title'],
                   self.G.nodes[node]['journal'],
                   self.G.nodes[node]['year'],
                   self.G.nodes[node]['authors'],
                   self.G.nodes[node]['citations_dois'],
                   self.G.nodes[node]['abstract']]
            row_list.append(row)
        self.df = pd.DataFrame(row_list, columns=cols)
        self.df.to_csv(filename+'.csv')



