#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx

D= {              #example_demand is a dictionary of dictionaries
"PE90TZL23":
            {
             "PE90ADN23": 170,
             "PE90PSK23": 250,
             "PE90ESY03": 310,
             "PE90SAM03": 320,
             "PE90GZM23": 220
            },
"PE90PSK23":
            {   
             "PE90ADN23": 140,
             "PE90TZL23": 270,
             "PE90ESY03": 230,
             "PE90SAM03": 210,
             "PE90GZM23": 250
             }
    }
