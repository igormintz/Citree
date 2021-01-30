# Citree
research citations tree visualization

    Citree is a class that creates a citations tree.
    the input is the DOI of the paper you want to start with (for example, 10.1002/ejp.1639).
    the data is retrieved using semanticscholar package
    (api that works with https://www.semanticscholar.org/).
    the network is built by using Networkx package.
    the plotting is done by using Bokeh package.
    
    attributes: 
    --------------
        first_doi - the doi provided by the user
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
    plot_html - creats an html file with tow plots:
        1. papers cictations tree
        2. authors who wrote toghather
    export_csv(filename='filename') - creates a dataframe and exports it as 'filename.csv'

----------------------------
    example of use:

    temp = Citree('10.1111/j.1526-4610.2006.00288.x')
    temp.first()
    temp.create_next_generation()
    temp.create_next_generation()
    temp.color_by_self_citation()
    temp.plot_html('temp')
