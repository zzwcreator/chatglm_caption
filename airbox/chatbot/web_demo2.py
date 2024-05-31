import time
import gradio as gr
import mdtex2html
from chat import TPUChatglm
import cpuinfo


# def postprocess(self, y):
#     if y is None:
#         return []
#     for i, (message, response) in enumerate(y):
#         y[i] = (
#             None if message is None else mdtex2html.convert((message)),
#             None if response is None else mdtex2html.convert(response),
#         )
#     return y


# gr.Chatbot.postprocess = postprocess

# glm = None

# cpu_info = cpuinfo.get_cpu_info()
# cpu_name = cpu_info['brand_raw']
# if cpu_name != "Apple M1 Pro":
#     glm = TPUChatglm()


# def parse_text(text):
#     """copy from https://github.com/GaiZhenbiao/ChuanhuChatGPT/"""
#     lines = text.split("\n")
#     lines = [line for line in lines if line != ""]
#     count = 0
#     for i, line in enumerate(lines):
#         if "```" in line:
#             count += 1
#             items = line.split('`')
#             if count % 2 == 1:
#                 lines[i] = f'<pre><code class="language-{items[-1]}">'
#             else:
#                 lines[i] = f'<br></code></pre>'
#         else:
#             if i > 0:
#                 if count % 2 == 1:
#                     line = line.replace("`", "\`")
#                     line = line.replace("<", "&lt;")
#                     line = line.replace(">", "&gt;")
#                     line = line.replace(" ", "&nbsp;")
#                     line = line.replace("*", "&ast;")
#                     line = line.replace("_", "&lowbar;")
#                     line = line.replace("-", "&#45;")
#                     line = line.replace(".", "&#46;")
#                     line = line.replace("!", "&#33;")
#                     line = line.replace("(", "&#40;")
#                     line = line.replace(")", "&#41;")
#                     line = line.replace("$", "&#36;")
#                 lines[i] = "<br>" + line
#     text = "".join(lines)
#     return text


# def gen(input, history):
#     i = 0
#     history.append((input, ''))

#     res = ''
#     while i < 4:
#         i += 1
#         res += str(i)
#         time.sleep(0.05)
#         history[-1] = (input, res)
#         yield res, history


# def predict(input, chatbot, max_length, top_p, temperature, history):
#     spilt = -1
#     if len(history) > 0:
#         while spilt >= -len(history):
#             prompt = ["[Round {}]\n\n问：{}\n\n答：{}\n\n".format(i + 1, x[0], x[1]) for i, x in enumerate(history[spilt:])]
#             if len("".join(prompt) + input) < 500:
#                 spilt -= 1
#             else:
#                 spilt += 1
#                 break
#     else:
#         spilt = 0

#     if spilt == 0:
#         history = []
#         if len(input) > 198:
#             input = input[:198]
#     else:
#         history = history[spilt:]
#     print(2222222222222222222222222)    
#     print(history)
#     print(33333333333333333333333333)
#     print(chatbot)
#     chatbot.append((parse_text(input), ""))
#     for response, history in glm.stream_predict(input, history):
#         chatbot[-1] = (parse_text(input), parse_text(response))
#         print(11111111111111111111)
#         print(input)
#         yield chatbot, history

#     # for response, history in gen(input, history):
#     #     chatbot[-1] = (parse_text(input), parse_text(response))
#     #     yield chatbot, history


# def reset_user_input():
#     return gr.update(value='')


# def reset_state():
#     return [], [], None


# with gr.Blocks() as demo:
#     gr.HTML("""<h1 align="center">ChatGLM2-6B TPU</h1>""")

#     chatbot = gr.Chatbot()
#     with gr.Row():
#         with gr.Column(scale=4):
#             with gr.Column(scale=12):
#                 user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10).style(
#                     container=False)
#             with gr.Column(min_width=32, scale=1):
#                 submitBtn = gr.Button("Submit", variant="primary")
#         with gr.Column(scale=1):
#             emptyBtn = gr.Button("Clear History")
#             max_length = gr.Slider(0, 32768, value=8192, step=1.0, label="Maximum length", interactive=True)
#             top_p = gr.Slider(0, 1, value=0.8, step=0.01, label="Top P", interactive=True)
#             temperature = gr.Slider(0, 1, value=0.95, step=0.01, label="Temperature", interactive=True)

#     history = gr.State([])

#     submitBtn.click(predict, [user_input, chatbot, max_length, top_p, temperature, history],
#                     [chatbot, history], show_progress=True)
#     submitBtn.click(reset_user_input, [], [user_input])

#     emptyBtn.click(reset_state, outputs=[chatbot, history], show_progress=True)

# demo.queue().launch(share=False, inbrowser=True, server_name="0.0.0.0")

# 模型初始化
glm = None
cpu_info = cpuinfo.get_cpu_info()
cpu_name = cpu_info['brand_raw']
if cpu_name != "Apple M1 Pro":
    glm = TPUChatglm()

print("finish model init")

max_length = 8192
top_p = 0.8
temperature = 0.95
history = []

while 1:
    msg = input("please input mingling")
    if msg == 'q':
        Ques = input("please input question：")
        for response, history in glm.stream_predict(Ques, history):
            print(response)
            



            
        # r = glm.stream_predict(Ques, history)
        # print(r)
