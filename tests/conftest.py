# Copyright (C) 2020-2022 Sebastian Blauth
#
# This file is part of cashocs.
#
# cashocs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cashocs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cashocs.  If not, see <https://www.gnu.org/licenses/>.
from collections import namedtuple
import pathlib

import fenics
import numpy as np
import pytest

import cashocs


@pytest.fixture()
def dir_path():
    return str(pathlib.Path(__file__).parent)


@pytest.fixture
def config_ocp(dir_path):
    return cashocs.load_config(f"{dir_path}/config_ocp.ini")


@pytest.fixture
def config_sop(dir_path):
    return cashocs.load_config(f"{dir_path}/config_sop.ini")


@pytest.fixture
def rng():
    return np.random.RandomState(300696)
