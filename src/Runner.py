"""
RL Framework
Authors: Arun Chaganty
Responsible for running agents and interacting with the Environment
"""

from Agent import *
from Environment import *
import Agents
import Environments

import pdb

class Runner:
    """Responsible for running agents and interacting with the environment"""
    def __init__(self, env):
        """
        @arg Agent
        @arg env
        """
        self.env = env

    @staticmethod
    def load_env( env_type, env_args ):
        """Try to construct an environment"""
        mod = __import__("Environments.%s"%(env_type), fromlist=[Environments])
        assert( hasattr(mod, env_type) )
        envClass = getattr( mod, env_type )
        env = envClass.create( *env_args )
        # except (ImportError, AssertionError):
        #     raise ValueError("Environment '%s' could not be found"%(env_type))
        # except (TypeError):
        #     raise ValueError("Environment '%s' could not be initialised\n%s"%(env_type, env.create.__doc__))

        return env

    @staticmethod
    def reload_env( env, env_type, env_args ):
        """Try to construct an environment"""
        mod = __import__("Environments.%s"%(env_type), fromlist=[Environments])
        assert( hasattr(mod, env_type) )
        envClass = getattr( mod, env_type )
        env = envClass.reset_rewards( env, *env_args )
        # except (ImportError, AssertionError):
        #     raise ValueError("Environment '%s' could not be found"%(env_type))
        # except (TypeError):
        #     raise ValueError("Environment '%s' could not be initialised\n%s"%(env_type, env.create.__doc__))

        return env

    @staticmethod
    def load_agent( env, agent_type, agent_args ):
        """Try to construct an agent"""

        mod = __import__("Agents.%s"%(agent_type), fromlist=[Agents])
        assert( hasattr(mod, agent_type) )
        agentClass = getattr( mod, agent_type )
        agent = agentClass( env.Q, *agent_args )
        # except (ImportError, AssertionError):
        #     raise ValueError("Agent '%s' could not be found"%(agent_type))
        # except (TypeError):
        #     raise ValueError("Agent '%s' could not be initialised\n%s"%(agent_type, agent.__init__.__doc__))

        return agent

    def run(self, agent, epochs):
        """ Simulate some epochs of running """

        state = self.env.start()
        reward = 0
        episode_ended = True
        ret = []
        decision_table = {}

        epoch = 0
        episode_epochs = decisions = 0
        started = False # Only collect after a while
        while epoch < epochs:
            action = agent.act(state, reward, episode_ended)
            decisions += 1
            state, reward, episode_ended = self.env.react(action)

            # Add rewards to ret
            if isinstance( action, Option ):
                # If this was an option, then multiple rewards would have been
                # returned.
                ret += reward
                epoch += len( state ) - 1
                episode_epochs += len( state ) - 1
            else:
                ret.append( reward )
                epoch += 1
                episode_epochs += 1

            if not started and epoch > int( epochs * 0.9 ):
                started = True
                decision_table = {}
                episode_epochs = decisions = 0

            if started and episode_ended:
                decisions_, count = decision_table.get( episode_epochs, (0,0) )
                decision_table[ episode_epochs ] = decisions_ + decisions, count+1
                episode_epochs = decisions = 0

        # Chop off any extras
        return ret[ : epochs ], decision_table

