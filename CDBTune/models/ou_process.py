#
# Copyright (c) 2017 Intel Corporation 
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import numpy as np


# Ornstein-Uhlenbeck process
class OUProcess:
    """
    OUProcess exploration policy is intended for continuous action spaces, and selects the action according to
    an Ornstein-Uhlenbeck process. The Ornstein-Uhlenbeck process implements the action as a Gaussian process, where
    the samples are correlated between consequent time steps.
    """
    def __init__(self, action_space, mu=0, theta=0.15, sigma=0.2, dt=0.01):
        """
        :param action_space: the action space used by the environment
        """
        self.action_space = action_space
        self.mu = float(mu) * np.ones(action_space)
        self.theta = float(theta)
        self.sigma = float(sigma) * np.ones(action_space)
        self.state = np.zeros(action_space)
        self.dt = dt

    def reset(self, sigma):
        self.sigma = sigma
        self.state = np.zeros(self.action_space)

    def noise(self):
        x = self.state
        dx = self.theta * (self.mu - x) * self.dt + self.sigma * np.random.randn(len(x)) * np.sqrt(self.dt)
        self.state = x + dx
        return self.state
