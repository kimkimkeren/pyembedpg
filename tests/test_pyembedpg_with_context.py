#
# Copyright 2015 Simulmedia, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import re
import psycopg2
from pyembedpg import PyEmbedPg


class TestPyEmbedPgWithContext(object):
    def setup(self):
        self.port = 15433

    def test_get_remote_version(self):
        pg = PyEmbedPg('test')
        last_version = pg.get_latest_remote_version()
        # can be 9.5.alpha1
        assert re.match('\d+\.[\w\.]+', last_version)

    def test_simple_run(self):
        pg = PyEmbedPg('9.4.0')
        with pg.start(self.port) as postgres:
            postgres.create_user('scott', 'tiger')
            postgres.create_database('testdb', 'scott')

            # Postgres is initialized, now run some queries
            with psycopg2.connect(database='postgres', user='scott', password='tiger', host='localhost', port=self.port) as conn:
                with conn.cursor() as cursor:
                    cursor.execute('CREATE TABLE employee(name VARCHAR(32), age INT)')
                    cursor.execute("INSERT INTO employee VALUES ('John', 32)")
                    cursor.execute("INSERT INTO employee VALUES ('Mary', 22)")
                    cursor.execute('SELECT * FROM employee ORDER BY age')
                    assert cursor.fetchall() == [('Mary', 22), ('John', 32)]

        # Test that the version is installed locally
        assert pg.get_latest_local_version() is not None
