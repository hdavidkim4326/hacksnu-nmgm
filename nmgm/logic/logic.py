from dataclasses import dataclass

"""
STEP 0 : preprocess all messages in chatrooms (message grouping, embeddings, metadata etc)
STEP 1 : cut chatroom into multiple threads (time, topic)
STEP 2 : generate chatroom analysis based on threads and topic
STEP 3 : generate user analysis based on chatroom data
STEP 4 : generate message edit features
"""