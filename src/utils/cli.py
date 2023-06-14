#!/usr/bin/python3

# Imports
import questionary
import os
import re

from questionary import Style, Validator, ValidationError
from .display import Display
from ..core.loader import CodeLoader
from ..core.embedder import CodeEmbedder
from ..core.analyzer import AnalyzeCode

## CLI Styler
custom_style = Style([
    ('separator', 'fg:#6C6C6C'),
    ('qmark', 'fg:#FF9D00 bold'),
    ('question', 'bold'),
    ('selected', 'fg:#5F819D'),
    ('pointer', 'fg:#FF9D00 bold'),
    ('choice', 'fg:#FF9D00 bold'),
    ('answer', 'fg:#5F819D bold'),
])

class CLI(object):
    def __init__(self):
        self.mode = ''
        
    def launc_main_cli(self):
        """
        Get mode
        """
        while True:
            Display.display_mode_description()
            self.mode = questionary.rawselect(
                "Select Mode:",
                choices=[
                    "Analyze",
                    "Develop",
                    "Exit"
                ],
                style=custom_style
                ).ask()

            if self.mode == "Exit":
                break
            
            if self.mode == "Analyze":
                self.handle_analyze_mode()
            
            elif self.mode == "Develop":
                self.handle_develop_mode()

    def handle_analyze_mode(self):
        '''
        Handles required parameters for this Analyze Mode
        '''
        Display.display_analyze_mode_description()       
        method = questionary.rawselect(
            "Please select a method for how you would like to provide your code:",
            choices=[
                "URL",
                "Directory Path",
                "Current directory",
                "Deeplake repo index",
                "Back"
            ],
            style=custom_style
            ).ask()

        if method == "Back":
            return

        # Handle the selected method
        if method == "URL":
            self.handle_url()

        elif method == "Directory Path":
            self.handle_path()
            
        elif method == "Current directory":
            self.handle_cwd()

        elif method == "Deeplake repo index":
            self.handle_deep_lake() 

    def handle_url(self):
        '''
        Gets URL and sends to loader
        '''
        repo_url = questionary.text(
            "Please provide a link to an online code repository",
            instruction="\n  Please use the following format\n  https://github.com/username/repo\n\n  URL: ",
            validate=URLValidator,
            style=custom_style
        ).ask()
        loader = CodeLoader()
        code_chunks = loader.load_online_repo(repo_url)
        self.embed_new(code_chunks)
    
    def handle_path(self):
        '''
        Gets Code Directory Path and sends to loader
        '''
        dir_path = questionary.path(
                "Please provide the path to the code directory",
                only_directories=True,
                style=custom_style
            ).ask()
        loader = CodeLoader()
        code_chunks = loader.load_directory(dir_path)
        self.embed_new(code_chunks)
        
    
    def handle_cwd(self):
        '''
        Launches loader that handles current directory
        '''
        loader = CodeLoader()
        code_chunks = loader.load_current_directory()
        self.embed_new(code_chunks)

    def handle_existing(self):
        pass

    def embed_new(self, chunks):
        '''
        Handles required parameters for creating a code index
        '''
        # Check for the ActiveLoop API key
        #if not os.getenv('ACTIVELOOP_TOKEN'):
        #    print("ActiveLoop API key not found. Please add it as an environment variable or to the .env file.")
        #    return

        # Prompt the user for their DeepLake username and hub name
        deeplake_info = questionary.prompt([
            {
                'type': 'text',
                'name': 'username',
                'message': "Please enter your DeepLake username: ",
            },
            {
                'type': 'text',
                'name': 'hub_name',
                'message': "Please enter the name of your DeepLake Index you'd like to create: ",
            }
            ],
            style=custom_style
        )

        username = deeplake_info['username']
        hub_name = deeplake_info['hub_name']

        embed = CodeEmbedder(hub_name, username)
        embed.embed_and_upload(chunks)
        analyzer = AnalyzeCode(username, hub_name)
        analyzer.interact()


    def retrieve_existing(self, chunks):
        pass
        
class URLValidator(Validator):
    '''
    Validate URL for Input
    '''
    def validate(self, document):
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        if not url_pattern.match(document.text):
            raise ValidationError(
                message="Please enter a valid URL",
                cursor_position=len(document.text))  # Move cursor to end