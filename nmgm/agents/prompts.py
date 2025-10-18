from textwrap import dedent

related_prompt = dedent(
        """
        <Role>
        You are a professional text analyst.
        </Role>

        <Task>
        Determine whether the two input chatlogs belong to the same thread or not.
        Consider semantics, time, and topic continuity.
        </Task>

        <Input>
        Chatlog 1: {msg1}
        Chatlog 2: {msg2}
        </Input>

        <Output Format>
        {{
            "related": bool
        }}
        </Output Format>
        """
        )


msg_analysis_prompt = dedent(
        """
        <Role>
        You are a professional text analyst.
        </Role>

        <Tasks>
        1. Determine the number of sentences in the input.
        2. Analyze the emotions in the input sentence and provide a score between 0 and 1 for each emotion: joy, sadness, anger, fear, surprise, disgust.
        3. Determine the speech type of the personality in the input sentence and provide a score between 0 and 1 for each type: directness, softness, emotionality, logicality, dominance, friendliness.
        </Tasks>

        For the speech type analysis, consider the following:

        1. Expressive : Direct, Emotional, Friendly, Dominant
            - 솔직하고 따뜻한 감정표현, 속도가 빠르고 에너지 높음.
            - 감탄사·이모지 ↑, 단문 직진형, “너무 좋다!!!”
        2. Instinctive : Direct, Emotional, Unfriendly, Dominant
            - 즉흥적 감정·불만 표현이 빠름. 선의여도 날카롭게 들릴 수 있음.
            - 명령·단정 “그건 아니야”, 반문·강조표현 ↑
        3. Commander : Direct, Logical, Dominant
            - 목표·효율 중심, 과업지향. 메시지 구조 선명.
            - “우선 A→B”, “데드라인”, 조건·절차·숫자 ↑
        4. Precisor : Direct, Logical, Neutral, Dominant
            - 팩트·정밀도 중시, 예외·세부조건을 명시.
            - “정확히”, “구체적으로”, “예외적으로” 등 세부 규정 ↑
        5. Harmonizer : Soft, Emotional, Friendly, Not-Dominant
            - 갈등 회피·관계 우선. 공감·배려 표현 풍부.
            - “혹시”, “괜찮다면”, “고마워/미안” ↑, 이모지 ↑
        6. Empathizer : Soft, Emotional, Friendly
            - 감정 읽기·언어 완충 탁월, 분위기 살림.
            - 반영문(“네 입장 이해”), 정서 라벨링(“답답했겠다”)
        7. Analyst : Soft, Logical Neutral, Not-Dominant
            - 데이터·근거 기반, 말투는 부드럽게.
            - “근거는…”, “데이터상”, 완곡+논리 접속사 동시 ↑
        8. Mediator : Soft, Logical, Friendly
            - 갈등 중재·프레이밍 능숙, 합의안 제시.
            - “한편/다만”, “둘 다 맞음”, “중간 제안” ↑

        <Input>
        {message}
        </Input>

        <Output Format>
        {{
            "emotions": [
                {{"emotion": "joy", "score": float}},
                {{"emotion": "sadness", "score": float}},
                {{"emotion": "anger", "score": float}},
                {{"emotion": "fear", "score": float}},
                {{"emotion": "surprise", "score": float}},
                {{"emotion": "disgust", "score": float}}
            ],
            "indices": [
                {{"index": "directness", "score": float}},
                {{"index": "softness", "score": float}},
                {{"index": "emotionality", "score": float}},
                {{"index": "logicality", "score": float}},
                {{"index": "dominance", "score": float}},
                {{"index": "friendliness", "score": float}}
            ],
            "num_sentences": int
        }}
        </Output Format>
        """)

thread_analysis_prompt = dedent("""
        <Role>
        You are a professional text analyst.
        </Role>

        <Task>
        1. Summarize content of the following messages in two sentences.
        2. Classify the chat type into one of the following categories: Decision Making & Planning, Sharing Emotions, Conflict Management, Information Exchange, Jokes/Chit-chat.
        </Task>

        <Input>
        {messages}
        </Input>

        <Output Format>
        {{
            "topic_summary": str,
            "chat_type": Literal["Decision Making", "Sharing Emotions", "Conflict Management", "Information Exchange", "Jokes and Chit-chat"]
        }}
        </Output Format>

        <Rules>
        Make sure the summary is in Korean.
        </Rules>
        """)

next_message_prompt = dedent("""
        <Role>
        You are a professional text analyst with a psychology background.
        </Role>
        Given the current chatroom situation, suggest an three appropriate alternate message suggestions for the user considering their personality type and the personality type of the other participant.

        <Input>
        Current User: {username} (Personality: {curr_personality})
        Recipient User: {other_username} (Personality: {other_personality})
        Latest Thread Topic: {latest_thread.topic_summary if latest_thread else "N/A"}
        Current Message: {message}
        </Input>

        <Previous Message Log>
        {message_log}
        </Previous Message Log>

        <Task>
        1. Analyze the current message and the personalities of both users.
        2. Suggest three alternate message options instead of the one given that aligns with the current user's personality type while considering the recipient's personality type.
        3. Minimize the risk of misunderstandings or conflicts based on personality differences.
        4. Provide a brief explanation for each suggestion on why it is appropriate.
        </Task>

        <Output Format>
        {{
            "suggested_message": str
            "reason": str
        }}
        """)

user_report_prompt = dedent("""
            <Role>
            You are a professional text analyst with a psychology background.
            </Role>

            Generate a user report based on the following metadata: {metadata}

            <Task>
            1. Classify the user's personality type into one of the following categories: 표현형, 본능형, 지시형, 정밀형, 조화형, 공감형, 분석형, 중재형.
            2. Summarize the user's overall texting style in two sentences.
            3. List three strengths and three weaknesses of the user's texting style.
            4. Evaluate the clarity of the user's sentences as 매우 높음, 높음, 보통, 낮음, or 매우 낮음.
            5. Provide three specific and actionable action plans for the user to improve their texting style.
                Do not include generic advice; tailor the suggestions to the user's personality type and texting habits.
                Focus on how to encode the messages so that others might understand them betters.
                Do not include actions plans outside of texting style improvement.
            </Task>
            
            For the personality type analysis, consider the following:

            1. Expressive : Direct, Emotional, Friendly, Dominant
                - 솔직하고 따뜻한 감정표현, 속도가 빠르고 에너지 높음.
                - 감탄사·이모지 ↑, 단문 직진형, “너무 좋다!!!”
            2. Instinctive : Direct, Emotional, Unfriendly, Dominant
                - 즉흥적 감정·불만 표현이 빠름. 선의여도 날카롭게 들릴 수 있음.
                - 명령·단정 “그건 아니야”, 반문·강조표현 ↑
            3. Commander : Direct, Logical, Dominant
                - 목표·효율 중심, 과업지향. 메시지 구조 선명.
                - “우선 A→B”, “데드라인”, 조건·절차·숫자 ↑
            4. Precisor : Direct, Logical, Neutral, Dominant
                - 팩트·정밀도 중시, 예외·세부조건을 명시.
                - “정확히”, “구체적으로”, “예외적으로” 등 세부 규정 ↑
            5. Harmonizer : Soft, Emotional, Friendly, Not-Dominant
                - 갈등 회피·관계 우선. 공감·배려 표현 풍부.
                - “혹시”, “괜찮다면”, “고마워/미안” ↑, 이모지 ↑
            6. Empathizer : Soft, Emotional, Friendly
                - 감정 읽기·언어 완충 탁월, 분위기 살림.
                - 반영문(“네 입장 이해”), 정서 라벨링(“답답했겠다”)
            7. Analyst : Soft, Logical Neutral, Not-Dominant
                - 데이터·근거 기반, 말투는 부드럽게.
                - “근거는…”, “데이터상”, 완곡+논리 접속사 동시 ↑
            8. Mediator : Soft, Logical, Friendly
                - 갈등 중재·프레이밍 능숙, 합의안 제시.
                - “한편/다만”, “둘 다 맞음”, “중간 제안” ↑
            

            <Rules>
            1. Generate the report in Korean.
            2. Ensure the report is concise and clear.
            3. Use bullet points for strengths, weaknesses, and action plans.
            </Rules>
            """
            )

summarize_all_threads_prompt = dedent("""
        Summarize the contents of the following threads in three sentences.text=
        
        <Input>
        {messages}
        </Input>

        Make sure the output is in Korean."""
        )

describe_personality_prompt = dedent("""
        Describe the texting style of the user with the following data with two sentences.
        And fill in the personality type among the following categories: 표현형, 본능형, 지시형, 정밀형, 조화형, 공감형, 분석형, 중재형.
        
        <Input>
        {metadata}
        </Input>

        For the personality type analysis, consider the following:

            1. Expressive : Direct, Emotional, Friendly, Dominant
                - 솔직하고 따뜻한 감정표현, 속도가 빠르고 에너지 높음.
                - 감탄사·이모지 ↑, 단문 직진형, “너무 좋다!!!”
            2. Instinctive : Direct, Emotional, Unfriendly, Dominant
                - 즉흥적 감정·불만 표현이 빠름. 선의여도 날카롭게 들릴 수 있음.
                - 명령·단정 “그건 아니야”, 반문·강조표현 ↑
            3. Commander : Direct, Logical, Dominant
                - 목표·효율 중심, 과업지향. 메시지 구조 선명.
                - “우선 A→B”, “데드라인”, 조건·절차·숫자 ↑
            4. Precisor : Direct, Logical, Neutral, Dominant
                - 팩트·정밀도 중시, 예외·세부조건을 명시.
                - “정확히”, “구체적으로”, “예외적으로” 등 세부 규정 ↑
            5. Harmonizer : Soft, Emotional, Friendly, Not-Dominant
                - 갈등 회피·관계 우선. 공감·배려 표현 풍부.
                - “혹시”, “괜찮다면”, “고마워/미안” ↑, 이모지 ↑
            6. Empathizer : Soft, Emotional, Friendly
                - 감정 읽기·언어 완충 탁월, 분위기 살림.
                - 반영문(“네 입장 이해”), 정서 라벨링(“답답했겠다”)
            7. Analyst : Soft, Logical Neutral, Not-Dominant
                - 데이터·근거 기반, 말투는 부드럽게.
                - “근거는…”, “데이터상”, 완곡+논리 접속사 동시 ↑
            8. Mediator : Soft, Logical, Friendly
                - 갈등 중재·프레이밍 능숙, 합의안 제시.
                - “한편/다만”, “둘 다 맞음”, “중간 제안” ↑
        Make sure the output is in Korean.
        """)

chatroom_report_prompt = dedent("""
            <Role>
            You are a professional text analyst with a psychology background.
            </Role>

            <Input>
            Metadata: {metadata}
            Candidate Warnings: {candidates}
            </Input>

            <Task>
            1. From the candidate warnings, identify and select up to three messages that are most likely to indicate a potential crisis situation.
            2. For each selected message, provide a brief detail of why it was chosen, focusing on key emotional indicators and context.
            3. Then provide an action plan to address the potential crisis, including immediate steps to take and longer-term strategies for support.
                Do not include generic advice; tailor the suggestions to the user's personality type and texting habits.
                Focus on how to encode the messages so that others might understand them betters.
                Do not include actions plans outside of texting style improvement.
            </Task>

            <Rules>
            Make sure the output is in Korean.
            </Rules>

""")