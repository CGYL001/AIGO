#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""运行特定的测试类"""

import unittest
from test_knowledge_base import TestMetadataStore

if __name__ == "__main__":
    print("运行元数据存储测试...")
    unittest.main(defaultTest='TestMetadataStore') 