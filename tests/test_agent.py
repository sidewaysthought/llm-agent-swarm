import unittest
import uuid
import os
import datetime
import dateutil.parser
from agent.main import Agent
from chat_api.main import ChatApi
from config_manager.main import ConfigManager


class TestAgent(unittest.TestCase):

    def setUp(self):

        # Prepare
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.config_file_path = os.path.join(self.current_directory, 'test_config.yaml')
        self.config_manager = ConfigManager(self.config_file_path)
        self.sign_on_template = str(self.config_manager.get_property('sign_on_template'))
        self.chat_api = ChatApi(host='https://127.0.0.1', port=5000)
        self.project = self.config_manager.get_project()
        self.agent_config = self.config_manager.get_agents()[0]
        self.session_id = str(uuid.uuid4())

        # Agent
        self.agent = Agent(self.chat_api, self.agent_config, self.project, self.session_id)

        # Sample Messages
        self.sample_messages = [
            {
                "from": 'Agent1',
                "to": 'ChiefExecAgent',
                "message": 'Message 1',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': 100
            },
            {
                "from": 'Agent2',
                "to": 'ChiefExecAgent',
                "message": 'Message 2',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': -1
            },
            {
                "from": None,
                "to": 'ChiefExecAgent',
                "message": 'Message 3',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': 100
            },
            {
                "from": 'Agent4',
                "to": None,
                "message": 'Message 4',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': 100
            },
            {
                "from": 'Agent5',
                "to": 'ChiefExecAgent',
                "message": None,
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': 100
            },
            {
                "from": 'Agent6',
                "to": 'ChiefExecAgent',
                "message": 'Message 6',
                'timestamp': None,
                'tokens': 100
            },
            {
                "from": 'Agent6',
                "to": 'ChiefExecAgent',
                "message": 'Message 6',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': None
            },
            {
            },
            {
                "from": '',
                "to": 'ChiefExecAgent',
                "message": 'Message 3',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': 100
            },
            {
                "from": 'Agent4',
                "to": '',
                "message": 'Message 4',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': 100
            },
            {
                "from": 'Agent5',
                "to": 'ChiefExecAgent',
                "message": '',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': 100
            },
            {
                "from": 'Agent6',
                "to": 'ChiefExecAgent',
                "message": 'Message 6',
                'timestamp': '',
                'tokens': 100
            },
            {
                "from": 'Agent6',
                "to": 'ChiefExecAgent',
                "message": 'Message 6',
                'timestamp': datetime.datetime.now().strftime(self.agent.TIME_FORMAT),
                'tokens': ''
            },
        ]


    #
    # Creating an agent
    #

    def test_create_agent(self):
        self.assertIsInstance(self.agent, Agent)

    # Chat API

    def test_create_agent_missing_chat_api(self):
        with self.assertRaises(Exception):
            agent = Agent({}, self.agent_config, self.project, self.session_id)

    def test_create_agent_none_chat_api(self):
        with self.assertRaises(Exception):
            agent = Agent(None, self.agent_config, self.project, self.session_id)

    def test_create_agent_string_chat_api(self):
        with self.assertRaises(Exception):
            agent = Agent('chat_api', self.agent_config, self.project, self.session_id)

    def test_create_agent_int_chat_api(self):
        with self.assertRaises(Exception):
            agent = Agent(123, self.agent_config, self.project, self.session_id)

    # Profile

    def test_create_agent_missing_profile(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, {}, self.project, self.session_id)

    def test_create_agent_none_profile(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, None, self.project, self.session_id)

    def test_create_agent_string_profile(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, 'profile', self.project, self.session_id)

    def test_create_agent_int_profile(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, 123, self.project, self.session_id)

    # Project

    def test_create_agent_missing_project(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, self.agent_config, {}, self.session_id)

    def test_create_agent_none_project(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, self.agent_config, None, self.session_id)

    def test_create_agent_int_project(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, self.agent_config, 123, self.session_id)

    # Session ID

    def test_create_agent_none_session_id(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, self.agent_config, self.project, None)

    def test_create_agent_int_session_id(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, self.agent_config, self.project, 123)

    def test_create_agent_dict_session_id(self):
        with self.assertRaises(Exception):
            agent = Agent(self.chat_api, self.agent_config, self.project, {})

    # Sign-on
    # When sign-on is completed, inbound_queue has exactly one element with keys message:str, 
    # to:str, from:str, timestamp:str and tokens:int.

    def test_sign_on(self):
        self.agent.sign_on()
        user_key = self.agent.SYSTEM_USER
        self.assertIn(user_key, self.agent.inbound_queue)
        self.assertEqual(len(self.agent.inbound_queue[user_key]), 1)
        queue = self.agent.inbound_queue[user_key]
        self.assertEqual(queue[0]['message'], 'Agent ChiefExecAgent has signed on.')
        self.assertEqual(queue[0]['to'], self.agent_config['name'])
        self.assertEqual(queue[0]['from'], user_key)
        self.assertIsInstance(queue[0]['timestamp'], str)
        self.assertIsInstance(queue[0]['tokens'], int)

    def test_sign_on_empty_message_template(self):
        agent = Agent(self.chat_api, self.agent_config, self.project, self.session_id)
        with self.assertRaises(Exception):
            agent.sign_on('')

    def test_sign_on_timestamp_is_correct_format(self):
        self.agent.sign_on()
        queue = self.agent.inbound_queue[self.agent.SYSTEM_USER]
        timestamp_format = self.agent.TIME_FORMAT
        timestamp = queue[0]['timestamp']
        parsed_timestamp = dateutil.parser.parse(timestamp)
        formatted_timestamp = parsed_timestamp.strftime(timestamp_format)
        self.assertEqual(timestamp, formatted_timestamp)

    # send_to_api
    # When send_to_api is called, since we're using a stub, a blank response is returned.

    def test_send_to_api(self):
        messages = [self.sample_messages[0], self.sample_messages[0]]
        response = self.agent.send_to_api(messages)
        self.assertEqual(response, '')

    def test_send_to_api_empty_message(self):
        with self.assertRaises(Exception):
            self.agent.send_to_api([])

    def test_send_to_api_one_message(self):
        response = self.agent.send_to_api([self.sample_messages[0]])
        self.assertEqual(response, '')

    def test_send_to_api_negative_tokens(self):
        message = self.sample_messages[1]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_none_from(self):
        message = self.sample_messages[2]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_none_to(self):
        message = self.sample_messages[3]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_none_message(self):
        message = self.sample_messages[4]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_none_timestamp(self):
        message = self.sample_messages[5]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_none_tokens(self):
        message = self.sample_messages[6]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])
    
    def test_send_to_api_empty_message_object(self):
        message = self.sample_messages[7]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_empty_string_from(self):
        message = self.sample_messages[8]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_empty_string_to(self):
        message = self.sample_messages[9]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_empty_string_message(self):
        message = self.sample_messages[10]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_empty_string_timestamp(self):
        message = self.sample_messages[11]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    def test_send_to_api_empty_string_tokens(self):
        message = self.sample_messages[12]
        with self.assertRaises(Exception):
            self.agent.send_to_api([message])

    # summarize
    # Because a api stub is being used, an empty string is returned

    def test_summarize(self):
        tokens = 100
        messages = [self.sample_messages[0], self.sample_messages[0]]
        response = self.agent.summarize(messages, tokens)
        self.assertEqual(response, '')

    def test_summarize_empty_messages(self):
        tokens = 100
        with self.assertRaises(Exception):
            self.agent.summarize([], tokens)

    def test_summarize_one_message(self):
        tokens = 100
        messages = [self.sample_messages[0]]
        response = self.agent.summarize(messages, tokens)
        self.assertEqual(response, '')

    def test_summarize_none_message(self):
        tokens = 100
        with self.assertRaises(Exception):
            self.agent.summarize(None, tokens)

    def test_summarize_empty_string_message(self):
        tokens = 100
        with self.assertRaises(Exception):
            self.agent.summarize('', tokens)

    def test_summarize_dict_message(self):
        tokens = 100
        with self.assertRaises(Exception):
            self.agent.summarize({'key', 'value'}, tokens)

    def test_summarize_negative_tokens(self):
        tokens = -100
        messages = [self.sample_messages[0], self.sample_messages[0]]
        with self.assertRaises(Exception):
            self.agent.summarize(messages, tokens)

    def test_summarize_none_tokens(self):
        tokens = None
        messages = [self.sample_messages[0], self.sample_messages[0]]
        with self.assertRaises(Exception):
            self.agent.summarize(messages, tokens)

    # fill_in_template

    def test_fill_in_template(self):
        filled_in_template = self.agent.fill_in_template(self.sign_on_template, self.agent.replacement_strings)
        self.assertEqual(filled_in_template, 'ChiefExecAgent, Test Project - Do a thing., Agent role., System, Guidance.')

    def test_fill_in_template_blank_template(self):
        filled_in_template = self.agent.fill_in_template('', self.agent.replacement_strings)
        self.assertEqual(filled_in_template, '')

    def test_fill_in_template_blank_replacement_strings(self):
        filled_in_template = self.agent.fill_in_template(self.sign_on_template, {})
        self.assertEqual(filled_in_template, self.sign_on_template)

    def test_fill_in_template_none_template(self):
        with self.assertRaises(Exception):
            self.agent.fill_in_template(None, self.agent.replacement_strings)

    def test_fill_in_template_none_replacement_strings(self):
        with self.assertRaises(Exception):
            self.agent.fill_in_template(self.sign_on_template, None)

    def test_fill_in_template_dict_template(self):
        with self.assertRaises(Exception):
            self.agent.fill_in_template({'key', 'value'}, self.agent.replacement_strings)

    # add_to_inbound_queue

    def test_add_to_inbound_queue(self):
        new_message = self.sample_messages[0]
        new_message['timestamp'] = None
        self.agent.add_to_inbound_queue(self.sample_messages[0], new_message['from'], 1)
        self.assertEqual(self.agent.inbound_queue, {new_message['from']: [new_message]})

    def test_add_to_inbound_queue_empty_message(self):
        new_message = {}
        with self.assertRaises(Exception):
            self.agent.add_to_inbound_queue(new_message, new_message['from'], 1)

    def test_add_to_inbound_queue_none_message(self):
        new_message = None
        with self.assertRaises(Exception):
            self.agent.add_to_inbound_queue(new_message, new_message['from'], 1)

    def test_add_to_inbound_queue_empty_string_from(self):
        new_message = self.sample_messages[0]
        with self.assertRaises(Exception):
            self.agent.add_to_inbound_queue(new_message, '', 1)

    def test_add_to_inbound_queue_none_from(self):
        new_message = self.sample_messages[0]
        with self.assertRaises(Exception):
            self.agent.add_to_inbound_queue(new_message, None, 1)

    def test_add_to_inbound_queue_empty_string_tokens(self):
        new_message = self.sample_messages[0]
        with self.assertRaises(Exception):
            self.agent.add_to_inbound_queue(new_message, new_message['from'], '')

    def test_add_to_inbound_queue_none_tokens(self):
        new_message = self.sample_messages[0]
        with self.assertRaises(Exception):
            self.agent.add_to_inbound_queue(new_message, new_message['from'], None)

    def test_add_to_inbound_queue_negative_tokens(self):
        new_message = self.sample_messages[0]
        with self.assertRaises(Exception):
            self.agent.add_to_inbound_queue(new_message, new_message['from'], -1)

    # receive

    def test_receive(self):
        self.agent.receive(self.sample_messages[0])
        sample_reply = {
            self.sample_messages[0]['from']: [
                self.sample_messages[0]
            ]
        }
        self.assertEqual(sample_reply, self.agent.inbound_queue)

    def test_receive_empty_message(self):
        with self.assertRaises(Exception):
            self.agent.receive({})

    def test_receive_none_message(self):
        with self.assertRaises(Exception):
            self.agent.receive(None)

    