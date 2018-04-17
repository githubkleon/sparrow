import click
import spproject as pj

@click.group()
def sparrow():
    pass

@click.command()
@click.option('--location', '-l', default=".", type=click.Path(exists=True))
@click.argument('project_name', default="project")
def create_project(project_name, location):
    """Create a new sparrow project. The default project name is project."""
    pj.create(project_name, location)
sparrow.add_command(create_project)


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
def add_file(file_path):
    """Add a file into project."""
    pj.addFile(file_path)
sparrow.add_command(add_file)

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
def remove_file(file_path):
    """Remove a file from project."""
    pj.removeFile(file_path)
sparrow.add_command(remove_file)

@click.command()
@click.option('--all/--non-all', '-a', default=False)
@click.argument('folder_path', type=click.Path(exists=True))
def add_folder(folder_path, all):
    """Add the files in a folder into project. -a for recursively addition."""
    pj.addFolder(folder_path, all)
sparrow.add_command(add_folder)

@click.command()
@click.option('--all/--non-all', '-a', default=False)
@click.argument('folder_path', type=click.Path(exists=True))
def remove_folder(folder_path, all):
    """Remove the files in a folder from project. -a for recursively reduction."""
    pj.removeFolder(folder_path, all)
sparrow.add_command(remove_folder)

@click.command()
@click.option('--verbose/--non-verbose', '-v', default=False)
@click.option('--include', '-i', default='.', type=click.Path(exists=True))
def compile(verbose, include):
    """Compile project from top file."""
    pj.compile(verbose, include)
sparrow.add_command(compile)

@click.command()
@click.argument('file_path', type=click.Path(exists=True))
def set_top(file_path):
    """Remove the files in a folder from project. -a for recursively reduction."""
    pj.setTopFile(file_path)
sparrow.add_command(set_top)

@click.command()
def top():
    """Quiry the top file."""
    pj.getTopFile()
sparrow.add_command(top)

@click.command()
def hierarchy():
    """Show project hierarchy."""
    pj.showHierarchy()
sparrow.add_command(hierarchy) 

# @click.command()
# def inspect():
#     click.echo("Inspecting project...")
# sparrow.add_command(inspect) 


@click.command()
def help():
    click.echo('''
usage: sparrow <command> [<args>]

Tpye sparrow for details.
''')
sparrow.add_command(help) 






