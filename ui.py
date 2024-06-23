import streamlit as st
from audio_recorder_streamlit import audio_recorder
import openai
import base64


def main():
    st.title("Speaking app")
    st.write("Hi there! Click on the voice recorder to interact with me. How can I assist you")
    recorded_audio = audio_recorder()


if __name__ == '__main__':
    main()
