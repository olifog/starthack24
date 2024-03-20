# <p align="center"> Canton of St. Gallen </p>

![St.Gallen](https://github.com/START-Hack/CantonOfStGallen_STARTHACK24/blob/98bb6ef9dbdeaeb5fc7fa611bccf5c0df75c14a5/Regierungsgeba%CC%88ude_CMS.jpg)

## <p align="center"> Case Introduction: </p>

**Problem**: The canton of St.Gallen faces the challenge that call volumes remain high despite new e-services and digital support requests. The expansion of the canton's range of services is in turn leading to more support requests. In addition to digital solutions in service management, the population and companies are also demanding rapid telephone assistance. To fulfil this demand, a voicebot is to be created as a scalable solution for improving telephone availability and automation.

**Expected Final Product**: The aim is to provide users with an efficient, accessible service while reducing staff workload. The dialogue and referral system should be able to answer queries independently and offer triage or referral options when required.

**Users**: Citizens, businesses, municipalities, partners, and other entities interacting with the Canton of St.Gallen.

##  <p align="center"> Data </p>
- Around 50 anonymised verbatim transcripts of real calls from the switchboard
- FAQ data from the website www.sg.ch
- Possibility to download .mp3 files directly from the cantonal website 
- Excel sheet with each link to each www.sg.ch subpage with FAQ as HTML (markdown from the HTML not sure yet)

##  <p align="center"> Resources: </p>
- We downloaded every single page from [sg.ch](https://sg.ch), covering 12 main sections as well as audio files with the voice recording reading the content of webpages. In total, it includes 3879 HTML pages, which requires around 400Mb of storage, and has 3492 unique MP3 recordings from `Vorlesen` (see the example here https://www.sg.ch/content/sgch/steuern-finanzen/steuern/formulare-wegleitungen/einkommens-vermoegenssteuer-privatpersonen.html). 
- All data is stored in a `data.zip` file that can be found on [Azure](https://djstarthackathon.blob.core.windows.net/data/data.zip). To get access to the data, download the `data.zip` and unzip with `unzip data.zip`.
- We organized `data` directory in such a way that it represents the hierarchy of web pages on the [sg.ch](https://sg.ch) website. In `st-gallen-data.xlsx` we collected for every webpage from [sg.ch](https://sg.ch) (1) the url of the page, (2) the local path to the scrapped HTML file of the webpage within `data` folder, and (3) the link to the `.mp3` file with the recorded voice.
- We also downloaded the `.mp3` recording reading the content of the page for every webpage where it was available. We stored `.mp3` in the corresponding directory under the name `audio.mp3`.
- Also if you need more detailed information about the scrapping process, refer to a Jupyter Notebooks in the repo: [scraping.ipynb](https://github.com/START-Hack/CantonOfStGallen_STARTHACK24/blob/main/scraping.ipynb) to [audio.ipynb](https://github.com/START-Hack/CantonOfStGallen_STARTHACK24/blob/main/audio.ipynb) to the audio files.

## <p align="center"> Technology </p>
The technologies that could be used to solve the case include artificial intelligence for language processing, natural language processing for understanding requests, web scraping tools for up-to-date information from the sg.ch website, machine learning to train the bots and a Speech2Text model (models via API are permitted).
Of course, other solution approaches (also in the low or no-code area) can also be used.

### Voicebot Technical Process

1. **Voice Input Processing**: The user's voice input is captured and sent to the Speech2Text model (e.g. Whisper API). 
2. **Text Transcription**: The Speech2Text model processes the speech input and transcribes it into text (including a variety of languages, accents and contexts that have been trained to ensure accurate transcription).
3. **Text Analysis and Response Generation**: The transcribed text is then forwarded to the language model (e.g. ChatGPT) for processing. The language model analyses the text, understands the context, questions or commands and generates an appropriate response based on its training data and capabilities.
4. **Transmission of Response**: The text response is then converted into natural-sounding speech using a text-to-speech (TTS) service.
5. **Reply and Inquiry**: a reply is sent back and a needs enquiry is made as to whether the request has been answered before the call is forwarded or ended.

### Integration Considerations
- Establishing a seamless connection between a Speech2Text model for speech-to-text transcription and a language model for text analysis and response generation. 
- User interface: Develop a user-friendly interface that allows for easy speech input and clear presentation of responses, whether in text and/or speech format.
- Privacy and security: Create a roadmap of how robust privacy protection could be implemented and what measures could be taken to protect users' voice data and transcripts while complying with relevant data protection regulations in a future version.

## <p align="center"> Use Case </p>
Participants are asked to demonstrate the functionality of the voicebot using a real telephone example (e.g. the word protocols provided, ideally in Swiss German). In addition, considerations should be made regarding implementation in the canton and compliance with data protection.

## <p align="center"> Judgment Criteria </p>

- **Functionality, Creativity, and Innovation** (40%)
  -	The voicebot is functional and can be tested live
  -	Novelty of the approach for a telephone exchange in the public administration of the Canton of St.Gallen
- **Presentation and Vision** (30%)
  -	Presentation of the bot and the project
  -	Development of a possible roadmap for the full deployment of the solution (incl. possible implementation partners and cost estimation)
- **Feasibility and Technical Assessment** (30%)
  -	Applicability in real scenarios within the telephone exchange of the canton of St.Gallen
  -	Realistic feasibility in terms of time, budget and data protection.
  -	Technical documentation and traceability are available

## <p align="center"> Presentation Prototype </p>
Participants must submit a PowerPoint (.pptx) presentation that outlines their concept, showcases their code, and ideally presents a working Minimum Viable Product (MVP).

## <p align="center"> Point of Contact </p>
- Beni Kunz, Project Manager Digital Services (Canton of St.Gallen)
- Sandro Parissenti, Program Manager Digital Transformation (Canton of St.Gallen)
- Lukas Möller (DeepJudge - Technical Partner)
- Alex Rivoire (DeepJudge - Technical Partner)
- Maksim Zubkov (DeepJudge - Technical Partner)

## <p align="center"> Prize for the Winning Team </p>
- Lunch with the State Secretary or a member of the cantonal government followed by a guided tour of the Canton of St.Gallen government building

OR
- a paragliding flight in the Canton of St.Gallen.
