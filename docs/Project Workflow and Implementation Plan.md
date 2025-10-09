

# **AdultingOS: A Prioritized Implementation Plan and Technical Workflow**

This document lays out the phased plan for building AdultingOS and the concrete steps to stand up the foundation quickly.

## Reader's guide (TL;DR)

- Phase 1: Establish the "steel thread" — Django + PostgreSQL + DRF, run migrations, and expose auth endpoints.
- Phase 2: Ship first AI features (Document Hub, Forecaster, Chatbot) behind authenticated APIs.
- Phase 3: Integrate features in the React Native UI and polish.

## Quickstart (Windows, PowerShell)

1) Always start in the project root and activate the virtual environment:

```powershell
cd C:\AdultingOS
.\venv\Scripts\Activate.ps1
```

2) Ensure PostgreSQL is installed and running locally for development. If not installed, download the Windows installer:
	https://www.postgresql.org/download/windows/

3) Create or update your backend .env (example):

```
POSTGRES_DB=adultingos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
DJANGO_SECRET_KEY=change-me
DEBUG=True
```

4) Apply initial database migrations:

```powershell
cd backend\adultingos_web
python manage.py migrate
```

5) Run the backend locally:

```powershell
python manage.py runserver 127.0.0.1:8001
```

Alternatively, use the VS Code task "Run Backend".

## **Section 1: Establishing the Application's Bedrock (Phase 1 Foundation)**

The initial phase is the most critical, focusing on the creation of a fully functional and secure "steel thread" that connects the mobile application to the database and back. This involves building the core, non-negotiable infrastructure for user management and API communication. By front-loading this foundational work, the most significant risks inherent in any client-server application are mitigated early in the development cycle, providing a stable platform upon which all subsequent features will be built.

### **1.1. Backend Scaffolding: Django, PostgreSQL, and DRF Setup**

The objective here is to initialize a clean, professional Django project correctly configured to use PostgreSQL for data persistence and the Django REST Framework (DRF) for building the API. This setup forms the backbone of the entire server-side application.

The process begins with establishing a Python virtual environment. This is a crucial best practice that isolates the project's dependencies, preventing conflicts with other projects or system-level packages.2 Once the environment is activated, the core packages can be installed using

pip: django for the web framework, psycopg2-binary to enable the connection to the PostgreSQL database, djangorestframework for the API toolkit, and python-dotenv for securely managing environment variables like database credentials and secret keys.3

With the dependencies installed, the Django project is created using the command django-admin startproject adultingos\_backend, followed by the creation of a primary application module with python manage.py startapp core.3 The

settings.py file must then be configured. The DATABASES setting should be modified to connect to the PostgreSQL instance, using environment variables loaded by python-dotenv to avoid hardcoding sensitive information like the password.2 

Additionally, rest\_framework and the newly created core app must be added to the INSTALLED\_APPS list to integrate them into the project.5

Finally, running the initial database migrations with python manage.py migrate will create Django's default tables, including those for its robust, built-in authentication system, within the PostgreSQL database, confirming that the connection is successful and the foundation is ready.2

### **1.2. The Keystone Service: Secure User Authentication API**

The gateway to the application is a secure and complete set of API endpoints for user registration, login, and profile management. For the prototype, a token-based authentication system is a standard and effective choice.

This implementation will leverage Django's powerful built-in User model, which provides a solid foundation for handling user accounts, permissions, and sessions out of the box.6 To expose this functionality via the API, Django REST Framework's

Serializers are used. A UserSerializer will define the data structure for user-related data, specifying which fields (e.g., username, email, password) are expected for registration and which are returned in API responses.5

The logic for handling user actions is encapsulated in APIView or ViewSet classes within the views.py file. These views will process incoming requests to create new users, validate login credentials, and issue authentication tokens upon successful login.5 DRF's built-in

TokenAuthentication provides a straightforward mechanism for this.

These views are then made accessible by wiring them up in the urls.py file, exposing endpoints such as /api/auth/register/, /api/auth/login/, and /api/profile/.5 A critical step is to secure the

/api/profile/ endpoint by requiring a valid authentication token for access. This is achieved by setting the appropriate permission\_classes on the view, ensuring that only authenticated users can retrieve their profile information and demonstrating a secure-by-default approach.5

### **1.3. Frontend Architecture: A Scalable React Native Structure**

To avoid future technical debt and facilitate a smooth development process, establishing a clean, maintainable, and scalable folder structure for the React Native application from the outset is paramount. A feature-based or hybrid project structure is superior for applications that are expected to grow, as it promotes modularity and separation of concerns.10

A recommended structure organizes the codebase within a primary /src directory:

* **/assets**: Contains static assets like images, custom fonts, and icons.11  
* **/components**: Houses globally reusable UI elements that are agnostic to any specific feature, such as a standardized Button.tsx, TextInput.tsx, or Card.tsx.10  
* **/features**: This is the core of the feature-based architecture. Each major feature of the application (e.g., /auth, /documents, /forecaster) resides in its own self-contained module. A typical feature folder will contain its own /screens, feature-specific /components, and any state management logic pertinent to that feature.12  
* **/navigation**: Centralizes the setup for the navigation library (e.g., React Navigation). This folder will define the navigation stacks, such as the authentication flow (Login, Register) versus the main application flow (Dashboard, Profile), and manage the transitions between them.10  
* **/services**: A dedicated home for all API interaction logic. This layer abstracts away the complexities of network requests. A library like axios is typically used to create a configured client that can handle all communication with the Django backend. Files like api.js or authService.ts will export functions for each endpoint (e.g., loginUser, fetchProfile).10  
* **/contexts** or **/store**: This directory is for global state management. It will hold the logic for storing application-wide state, such as the user's authentication token and profile information, making it accessible to all components that need it.10

### **1.4. Establishing the Connection: The First Authenticated API Call**

The final step in building the foundation is to verify that the entire stack—from the mobile client to the backend server and database—is working in concert. This is achieved by implementing the full user authentication flow: registering a user, logging in from the React Native app, and fetching their profile data from a protected Django endpoint.

This process begins by building the registration and login screens within the /features/auth/screens directory of the React Native project. When a user submits their credentials, the application will use the axios instance defined in the /services layer to make POST requests to the /api/auth/register/ and /api/auth/login/ endpoints on the Django server.16

Upon a successful login response, the backend will return an authentication token. The mobile app must then securely store this token on the device, for example, using a library like AsyncStorage. This token is also placed into the global state so that it can be used for subsequent authenticated requests.

The connection is validated by making a GET request to the protected /api/profile/ endpoint. This request must include the stored token in the Authorization header, typically in the format Authorization: Token \<user\_token\>. If the backend successfully authenticates the token and returns the user's profile data, that data can be displayed on a basic profile screen in the app. This successful round trip confirms that the end-to-end connection is secure and functional, providing a stable base for building the application's core features.

A decoupled architecture with a separate frontend and backend introduces the risk of miscommunication. The API serves as a contract between the two systems; any uncoordinated change on one side can break the other. This is particularly risky during parallel development phases.1 To mitigate this, the structure of all API endpoints—including URLs, request bodies, response formats, and permissions—must be formally defined before implementation. This "API contract" acts as the single source of truth for all client-server communication.

| Endpoint (URL) | HTTP Method | Description | Permissions | Request Body (JSON) | Success Response (JSON) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| /api/auth/register/ | POST | Creates a new user account. | Public | {"username": "...", "email": "...", "password": "..."} | {"user\_id": 1, "username": "...", "email": "..."} |
| /api/auth/login/ | POST | Authenticates a user and returns a token. | Public | {"username": "...", "password": "..."} | {"token": "..."} |
| /api/profile/ | GET | Retrieves the profile of the authenticated user. | Authenticated | (None) | {"username": "...", "email": "...", "first\_name": "..."} |

## **Section 2: Building the Data and Intelligence Core (Phase 1 & 2 Overlap)**

With the user management system in place, the focus shifts to the application's core value proposition: data and intelligence. This section covers the acquisition of the raw data that powers the app's recommendations and the implementation of the first, and arguably most crucial, AI feature: the Document Intelligence Hub.

### **2.1. Data Acquisition and Structuring**

The objective is to gather benefit information from official Canadian government websites, clean it, and structure it within the PostgreSQL database to form the app's knowledge base.1

For this task, a combination of **Scrapy** and **BeautifulSoup** is recommended. Scrapy provides a powerful and scalable framework for crawling websites and managing the scraping process, while BeautifulSoup excels at parsing complex or poorly formatted HTML, allowing for a robust and flexible data extraction pipeline.18 The process must adhere to ethical scraping guidelines, which include respecting the

robots.txt file of the target websites, scheduling scraping activities during off-peak hours to minimize server load, and using an appropriate user agent string.19

The implementation process involves several steps:

1. **Define a Scrapy Item**: This is a Python class that defines the structure of the data to be collected for each benefit, with fields such as name, description, eligibility\_rules\_text, and source\_url.  
2. **Write a Scrapy Spider**: This class contains the logic for crawling the target government sites (Canada Revenue Agency, Employment and Social Development Canada, etc.). The spider starts at a specified URL and follows links to find pages containing benefit information.  
3. **Parse HTML**: Within the spider's parse method, BeautifulSoup is used to navigate the HTML structure of each page and extract the relevant text from specific tags (e.g., \<h1\> for the benefit name, \<p\> for the description).20  
4. **Create a Scrapy Pipeline**: After a spider extracts an item, it is passed to a pipeline. The pipeline contains a series of processing steps to clean the data (e.g., removing extra whitespace, standardizing formats) and then save the structured information to the PostgreSQL database using Django's Object-Relational Mapper (ORM).

To support this, a corresponding Benefit model must be defined in the Django models.py file. This model will mirror the structure of the Scrapy Item, creating the necessary table and columns in the database to store the scraped data.

### **2.2. Implementing the Document Intelligence Hub (PoC)**

This feature is a core component of AdultingOS, designed to create a backend service that allows an authenticated user to upload a document (like a W-2), processes it using Optical Character Recognition (OCR) and Named Entity Recognition (NER), and returns structured key-value pairs.1

First, a new API endpoint, /api/documents/upload/, must be defined. This will be a POST request that requires user authentication. Django REST Framework's FileUploadParser can be used to handle the incoming image file securely. For scalability and security, the uploaded file should be stored in a service like AWS S3, as specified in the project's technology stack.1

The OCR process will be handled by **Tesseract**. After installing the pytesseract library and the Tesseract engine itself 22, the backend service will use the

Pillow library to open the uploaded image. A critical step for improving OCR accuracy is image preprocessing. Techniques such as converting the image to grayscale are essential best practices that significantly enhance the quality of the text extraction.23 The preprocessed image is then passed to the

pytesseract.image\_to\_string() function to extract the raw text.23

The performance of all subsequent AI features is fundamentally limited by the quality of their input data. For the Document Hub, if the OCR process produces garbled or inaccurate text due to poor image quality, the NER step will fail to identify the correct entities.22 Similarly, if the web-scraped benefits data is messy or inconsistent, the eligibility forecaster will lack a reliable ground truth for training. Therefore, dedicating development time to data preprocessing and cleaning is not an optional refinement; it is a prerequisite for success. This means implementing image enhancement steps (grayscale, binarization) as a mandatory part of the OCR pipeline and writing robust cleaning functions within the Scrapy pipeline to standardize data before it enters the database.

Once the raw text is extracted, **spaCy** is used for NER. After installing spacy and downloading a pre-trained English model like en\_core\_web\_sm 26, the model is loaded with

nlp \= spacy.load("en\_core\_web\_sm").27 The raw text from Tesseract is processed by passing it to the

nlp object. The service then iterates through the resulting doc.ents to identify and label named entities such as MONEY (for income figures), DATE, PERSON, and ORG (organization names).27

Finally, the extracted entities are structured into a clean JSON response (e.g., {"gross\_income": {"value": 50000, "type": "MONEY"}, "employer": {"value": "ABC Corp", "type": "ORG"}}) and returned to the React Native client, providing the user with the structured data from their document.

## **Section 3: Developing Advanced AI Capabilities in Parallel (Phase 2\)**

With the core application infrastructure and the first AI feature established, development can proceed on the remaining AI services. As outlined in the project plan, these can be built as independent modules within the Django application, allowing for parallel workstreams.1

### **3.1. The Proactive Eligibility Forecaster (PoC)**

The objective is to build a machine learning model that predicts a user's likelihood of approval for a given benefit based on their profile data. A key challenge for this proof-of-concept is the lack of a real-world labeled dataset. As noted in the project proposal, this requires the generation of simulated data for training.1

A Python script will be created to generate a realistic synthetic dataset. This involves:

1. **Defining a Schema**: The dataset will include columns based on common eligibility criteria, such as income, age, residency\_status, is\_student, has\_dependents, credit\_score\_range, and the target variable, is\_approved (a binary 0 or 1).  
2. **Generating Data**: Using libraries like pandas and numpy, several thousand rows of synthetic data will be generated. To make the data realistic, logical correlations will be introduced; for instance, higher income and better credit scores will be positively correlated with a higher probability of loan approval.29  
3. **Saving the Dataset**: The generated data will be saved as a CSV file, which will serve as the training data for the model.

The model training process should be kept separate from the live Django application code to maintain a clean architecture. A Jupyter Notebook or a standalone Python script is ideal for this task. The workflow is as follows:

1. Load the synthetic CSV data using pandas.  
2. Perform necessary preprocessing, such as one-hot encoding for categorical features (e.g., residency\_status) and scaling for numerical features (e.g., income).  
3. Train a simple classification model from the scikit-learn library, such as LogisticRegression or RandomForestClassifier.32  
4. Serialize the trained model into a single file using joblib or pickle. This .pkl file is the model artifact that will be used for predictions.8

The process of training a machine learning model is computationally intensive and iterative, involving data loading, preprocessing, and fitting algorithms. This process should not be part of the live web application's codebase. A Django web server is designed to handle HTTP requests quickly and efficiently.8 Mixing training code with API logic bloats the application, introduces unnecessary dependencies, and complicates deployment, as any change to the model would require redeploying the entire web application. The correct workflow is to train the model in a separate, offline environment. The

*only* artifact of this process should be the serialized model file (e.g., model.pkl). The Django application's role is solely to load this pre-trained file and use it for inference. This separation of concerns is a fundamental MLOps principle that is critical for maintainability, even in a prototype.8

Finally, a new API endpoint, /api/benefits/forecast/, will be created. The corresponding view in Django will load the saved .pkl model. When a request containing user data arrives, the view will preprocess the input data in the same way as the training data, pass it to the model.predict\_proba() method, and return the resulting approval probability as a JSON response.36

### **3.2. The Conversational Guidance Navigator (PoC)**

This feature involves creating a chatbot service that leverages a third-party Large Language Model (LLM) to answer user questions about financial benefits and terms.1

The first step is to manage the LLM API key securely. It should be stored as an environment variable and accessed through the Django settings.py file, following the same security practice used for the database password.38

An API endpoint, /api/chatbot/ask/, will be defined to handle user queries. The backend view for this endpoint will receive a user's question from the request body. It will then construct a carefully engineered prompt to send to the LLM. This "prompt engineering" is crucial to constrain the LLM's responses and prevent misuse. A good prompt might be: You are a helpful assistant for the AdultingOS app. Your role is to answer questions about Canadian financial benefits and terms. Do not answer questions outside this topic. The user's question is: "{user\_question}".

The view will then use a library like requests or the LLM provider's official Python client to make an API call to the external service.38 After receiving the response, it will parse the answer and return the text in a JSON object to the frontend.

Third-party LLM APIs are external dependencies that can be slow, expensive, and unpredictable. They introduce risks like network latency, rate limits, and the potential for irrelevant responses. A naive implementation that blocks a web request while waiting for the LLM can lead to a poor user experience. Therefore, the application must be architected to be resilient. Implementing an aggressive caching layer, using a tool like Redis managed by Django's caching framework, is not merely a performance optimization but a critical architectural pattern to manage costs and improve reliability by storing answers to common questions.38 For a production-grade system, this task would be offloaded to a background worker queue like Celery to prevent blocking the main web server thread.38

## **Section 4: Final Integration and Strategic Workflow (Phase 3\)**

The final phase of the project focuses on bringing all the developed components together into a cohesive user experience within the React Native application. This involves building the frontend interfaces for the AI services and implementing the remaining features. This section culminates in a definitive, prioritized roadmap that summarizes the entire development journey, providing a clear checklist for completion.

### **4.1. Frontend Feature Integration**

The objective is to build the React Native screens and components that allow users to interact with the newly created AI-powered API endpoints.

* **Document Hub UI**: A new screen will be created within the /features/documents/ module. This screen will utilize a library like react-native-document-picker to allow users to select an image file from their device. The selected file will then be sent in a POST request to the /api/documents/upload/ endpoint. Upon receiving the response, the app will parse the structured JSON data and display it to the user in a clear, readable format.  
* **Forecaster UI**: On the screen that lists available benefits, a "Check Eligibility" button will be added for each item. When tapped, this button will trigger an API call to the /api/benefits/forecast/ endpoint, sending the user's relevant profile data. The returned approval probability will be displayed to the user, perhaps as a percentage or a simple gauge, providing immediate feedback.  
* **Chatbot UI**: A simple chat interface will be built in a /features/chatbot/ module. This will consist of a text input field for the user's question and a scrollable view to display the conversation history. Each time the user submits a message, the app will make a POST request to the /api/chatbot/ask/ endpoint and append the LLM's response to the conversation view.

### **4.2. Implementing the "Benefit-to-Goal" Planner**

As noted in the project proposal, this feature has a relatively low technical complexity but offers a medium-to-high impact on user value by enhancing engagement and making the benefits feel more tangible.1

The implementation will require work on both the backend and frontend:

* **Backend**: A new Goal model will be created in Django's models.py, linked to the User model via a foreign key. A set of simple CRUD (Create, Read, Update, Delete) API endpoints will be developed under the /api/goals/ path to allow the client to manage these goals.  
* **Frontend**: A "Goals" screen will be created where users can add, view, and edit their personal financial goals (e.g., "Save for Emergency Fund," "Pay Off Student Loan"). On the main benefits display screen, an option will be provided for users to link a specific benefit to one of their goals, visually demonstrating how claiming that benefit contributes to their financial progress.

### **4.3. The Definitive Workflow and Path to Completion**

This section synthesizes the entire report into a final, prioritized checklist. This roadmap directly addresses the core query about what to work on first and what to worry about last, providing a clear and actionable master plan to ensure all "In-Scope" items are completed by the December 2025 deadline.1

| Priority | Task | Phase | Key Dependencies | Rationale & Notes |
| :---- | :---- | :---- | :---- | :---- |
| **P1** | Setup Django Backend & PostgreSQL DB | 1 | None | The absolute foundation of the entire application. Must be done first. |
| **P2** | Implement User Authentication API Endpoints | 1 | P1 | All other features require an authenticated user. This is the gateway to the app. |
| **P3** | Setup React Native Frontend Structure | 1 | None (Parallel to P1/P2) | A clean structure now prevents major refactoring later. Can start immediately. |
| **P4** | First Authenticated API Call (RN \-\> Django) | 1 | P2, P3 | Confirms the entire foundational stack is working before adding complexity. |
| **P5** | Scrape & Structure Benefits Data | 1/2 | P1 | The application's core dataset. The app is not useful without this information. |
| **P6** | Implement Document Intelligence Hub API | 1/2 | P2 | Highest value AI feature. Tackle it once the foundation is stable and secure. |
| **P7** | Implement Eligibility Forecaster API | 2 | P2 | Can be developed in parallel with other features once user auth is complete. |
| **P8** | Implement Chatbot Navigator API | 2 | P2 | Can be developed in parallel. Relies on external API, decoupling it from core logic. |
| **P9** | Integrate All AI Features into RN UI | 3 | P6, P7, P8 | Final integration step, bringing the backend services to life for the user. |
| **P10** | Implement "Benefit-to-Goal" Planner | 3 | P2 | Lower complexity; a good feature to add once the core AI functionality is proven. |
| **P11** | User Acceptance Testing (UAT) & Bug Fixing | 3 | All previous tasks | Final validation step as per the project plan to gather feedback and polish the prototype.1 |

## **Conclusion**

The successful development of the AdultingOS prototype hinges on a structured and prioritized workflow. This report has outlined a clear, phase-by-phase implementation plan that addresses the project's technical requirements while mitigating common development risks.

The recommended path begins with establishing a robust application foundation, including the backend server, database, and secure user authentication system, connected to a well-structured mobile frontend. This "steel thread" approach ensures the core infrastructure is sound before layering on more complex features. Subsequent phases focus on developing the core AI capabilities—the Document Intelligence Hub, the Proactive Eligibility Forecaster, and the Conversational Guidance Navigator—in a modular fashion that allows for parallel workstreams. The final phase concentrates on integrating these services into a cohesive user experience within the React Native application and completing the final features.

By adhering to the architectural principles discussed—defining a clear API contract, prioritizing data quality, decoupling model training from serving, and managing external dependencies resiliently—the project can proceed with a high degree of confidence. The provided prioritized roadmap serves as a master checklist to guide development, ensuring that all "In-Scope" objectives are met, culminating in a functional prototype ready for user acceptance testing by the December 2025 deadline.

#### **Works cited**

1. project proposal adulting os.docx  
2. How to use PostgreSQL with Django \- EDB, accessed September 25, 2025, [https://www.enterprisedb.com/postgres-tutorials/how-use-postgresql-django](https://www.enterprisedb.com/postgres-tutorials/how-use-postgresql-django)  
3. Building a Scalable Authentication System with Django and PostgreSQL \- Medium, accessed September 25, 2025, [https://medium.com/@iampankajk/building-a-scalable-authentication-system-with-django-and-postgresql-c96cc88b4b1d](https://medium.com/@iampankajk/building-a-scalable-authentication-system-with-django-and-postgresql-c96cc88b4b1d)  
4. React Native and Django for Beginners — Crowdbotics, accessed September 25, 2025, [https://crowdbotics.com/posts/blog/react-native-django-for-beginners/](https://crowdbotics.com/posts/blog/react-native-django-for-beginners/)  
5. Quickstart \- Django REST framework, accessed September 25, 2025, [https://www.django-rest-framework.org/tutorial/quickstart/](https://www.django-rest-framework.org/tutorial/quickstart/)  
6. User authentication in Django, accessed September 25, 2025, [https://docs.djangoproject.com/en/5.2/topics/auth/](https://docs.djangoproject.com/en/5.2/topics/auth/)  
7. Django Tutorial Part 8: User authentication and permissions \- Learn web development, accessed September 25, 2025, [https://developer.mozilla.org/en-US/docs/Learn\_web\_development/Extensions/Server-side/Django/Authentication](https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Server-side/Django/Authentication)  
8. How I Built a Machine Learning API with Django REST Framework in 10 Days, accessed September 25, 2025, [https://python.plainenglish.io/how-i-built-a-machine-learning-api-with-django-rest-framework-in-10-days-08b2b28bda0b](https://python.plainenglish.io/how-i-built-a-machine-learning-api-with-django-rest-framework-in-10-days-08b2b28bda0b)  
9. How To Make a Django REST API \- Full Tutorial & Deployment \- YouTube, accessed September 25, 2025, [https://www.youtube.com/watch?v=t-uAgI-AUxc](https://www.youtube.com/watch?v=t-uAgI-AUxc)  
10. Best Practices for Structuring a React Native TypeScript Project | by ..., accessed September 25, 2025, [https://blog.stackademic.com/best-practices-for-structuring-a-react-native-typescript-project-aff471741185](https://blog.stackademic.com/best-practices-for-structuring-a-react-native-typescript-project-aff471741185)  
11. How to Organize Your Components in React Native: Folder Structure and Project Organization \- DEV Community, accessed September 25, 2025, [https://dev.to/paulocappa/how-to-organize-your-components-in-react-native-folder-structure-and-project-organization-1hke](https://dev.to/paulocappa/how-to-organize-your-components-in-react-native-folder-structure-and-project-organization-1hke)  
12. Best Practices for Structuring Your React Native Projects | by DhineshKumar Thirupathi, accessed September 25, 2025, [https://medium.com/@dhidroid/best-practices-for-structuring-your-react-native-projects-1f9552a6c781](https://medium.com/@dhidroid/best-practices-for-structuring-your-react-native-projects-1f9552a6c781)  
13. Project Structure \- React Native Express, accessed September 25, 2025, [https://www.reactnative.express/app/project\_structure](https://www.reactnative.express/app/project_structure)  
14. React Native project structure: a best practices guide \- Tricentis, accessed September 25, 2025, [https://www.tricentis.com/learn/react-native-project-structure](https://www.tricentis.com/learn/react-native-project-structure)  
15. A tutorial for React Native app with Django Backend. : r/reactnative \- Reddit, accessed September 25, 2025, [https://www.reddit.com/r/reactnative/comments/phah7o/a\_tutorial\_for\_react\_native\_app\_with\_django/](https://www.reddit.com/r/reactnative/comments/phah7o/a_tutorial_for_react_native_app_with_django/)  
16. What are the possible ways to integrate react and django \- Reddit, accessed September 25, 2025, [https://www.reddit.com/r/django/comments/12jghzi/what\_are\_the\_possible\_ways\_to\_integrate\_react\_and/](https://www.reddit.com/r/django/comments/12jghzi/what_are_the_possible_ways_to_integrate_react_and/)  
17. Creating React Native apps with Django rest-api | by Hassan Abid | Medium, accessed September 25, 2025, [https://medium.com/@hassanabid/creating-react-native-apps-with-django-rest-api-59e8417865e9](https://medium.com/@hassanabid/creating-react-native-apps-with-django-rest-api-59e8417865e9)  
18. Scrapy vs. Beautiful Soup: A Comparison of Web Scraping Tools \- Oxylabs, accessed September 25, 2025, [https://oxylabs.io/blog/scrapy-vs-beautifulsoup](https://oxylabs.io/blog/scrapy-vs-beautifulsoup)  
19. Web scraping, accessed September 25, 2025, [https://www.statcan.gc.ca/en/our-data/where/web-scraping](https://www.statcan.gc.ca/en/our-data/where/web-scraping)  
20. Web-scraping using BeautifulSoup \- Medium, accessed September 25, 2025, [https://medium.com/@ritupd/web-scraping-countries-and-population-data-using-beautifulsoup-14f8b740c179](https://medium.com/@ritupd/web-scraping-countries-and-population-data-using-beautifulsoup-14f8b740c179)  
21. Screen Scraping Government Data with Python | At These Coordinates, accessed September 25, 2025, [https://atcoordinates.info/2025/04/21/screen-scraping-government-data-with-python/](https://atcoordinates.info/2025/04/21/screen-scraping-government-data-with-python/)  
22. Python OCR Tutorial: Tesseract, Pytesseract, and OpenCV \- Nanonets, accessed September 25, 2025, [https://nanonets.com/blog/ocr-with-tesseract/](https://nanonets.com/blog/ocr-with-tesseract/)  
23. Python Tesseract OCR: Extract text from images using pytesseract \- Nutrient, accessed September 25, 2025, [https://www.nutrient.io/blog/how-to-use-tesseract-ocr-in-python/](https://www.nutrient.io/blog/how-to-use-tesseract-ocr-in-python/)  
24. Reading Text from the Image using Tesseract \- GeeksforGeeks, accessed September 25, 2025, [https://www.geeksforgeeks.org/python/reading-text-from-the-image-using-tesseract/](https://www.geeksforgeeks.org/python/reading-text-from-the-image-using-tesseract/)  
25. How to use Tesseract OCR in a Python script (pytesseract) \- YouTube, accessed September 25, 2025, [https://www.youtube.com/watch?v=HNCypVfeTdw](https://www.youtube.com/watch?v=HNCypVfeTdw)  
26. spaCy 101: Everything you need to know, accessed September 25, 2025, [https://spacy.io/usage/spacy-101](https://spacy.io/usage/spacy-101)  
27. Python | Named Entity Recognition (NER) using spaCy ..., accessed September 25, 2025, [https://www.geeksforgeeks.org/python/python-named-entity-recognition-ner-using-spacy/](https://www.geeksforgeeks.org/python/python-named-entity-recognition-ner-using-spacy/)  
28. Named Entity Recognition (NER) in Python with Spacy \- Analytics Vidhya, accessed September 25, 2025, [https://www.analyticsvidhya.com/blog/2021/06/nlp-application-named-entity-recognition-ner-in-python-with-spacy/](https://www.analyticsvidhya.com/blog/2021/06/nlp-application-named-entity-recognition-ner-in-python-with-spacy/)  
29. Loan Eligibility Prediction using Machine Learning Models in Python \- GeeksforGeeks, accessed September 25, 2025, [https://www.geeksforgeeks.org/machine-learning/loan-eligibility-prediction-using-machine-learning-models-in-python/](https://www.geeksforgeeks.org/machine-learning/loan-eligibility-prediction-using-machine-learning-models-in-python/)  
30. Loan Prediction Problem From Scratch to End \- Analytics Vidhya, accessed September 25, 2025, [https://www.analyticsvidhya.com/blog/2022/05/loan-prediction-problem-from-scratch-to-end/](https://www.analyticsvidhya.com/blog/2022/05/loan-prediction-problem-from-scratch-to-end/)  
31. Loan Eligibility Prediction \- Machine Learning \- Kaggle, accessed September 25, 2025, [https://www.kaggle.com/code/vikasukani/loan-eligibility-prediction-machine-learning](https://www.kaggle.com/code/vikasukani/loan-eligibility-prediction-machine-learning)  
32. Loan Eligibility Prediction using Python \- Kaggle, accessed September 25, 2025, [https://www.kaggle.com/code/durgadulal/loan-eligibility-prediction-using-python](https://www.kaggle.com/code/durgadulal/loan-eligibility-prediction-using-python)  
33. datamugger/Loan-Eligibility-Prediction-Data-Science-Project \- GitHub, accessed September 25, 2025, [https://github.com/datamugger/Loan-Eligibility-Prediction-Data-Science-Project](https://github.com/datamugger/Loan-Eligibility-Prediction-Data-Science-Project)  
34. Predicting Possible Loan Default Using Machine Learning \- Analytics Vidhya, accessed September 25, 2025, [https://www.analyticsvidhya.com/blog/2022/04/predicting-possible-loan-default-using-machine-learning/](https://www.analyticsvidhya.com/blog/2022/04/predicting-possible-loan-default-using-machine-learning/)  
35. How to deploy a scikit learn regression model as a web service? \- Microsoft Q\&A, accessed September 25, 2025, [https://learn.microsoft.com/en-us/answers/questions/526203/how-to-deploy-a-scikit-learn-regression-model-as-a](https://learn.microsoft.com/en-us/answers/questions/526203/how-to-deploy-a-scikit-learn-regression-model-as-a)  
36. A Quick Guide to Deploy your Machine Learning Models using Django and Rest API, accessed September 25, 2025, [https://www.aionlinecourse.com/blog/deploy-machine-learning-model-using-django-and-rest-api](https://www.aionlinecourse.com/blog/deploy-machine-learning-model-using-django-and-rest-api)  
37. Machine learning Model Serving with Django Rest Framework | by Shanaka Chathuranga, accessed September 25, 2025, [https://medium.com/@shanakachathuranga/machine-learning-model-serving-with-django-rest-framework-397f495a8a38](https://medium.com/@shanakachathuranga/machine-learning-model-serving-with-django-rest-framework-397f495a8a38)  
38. Integrating Django with AI and LLMs: Building AI-Powered Web Apps | by Aashish Kumar, accessed September 25, 2025, [https://aashishkumar12376.medium.com/integrating-django-with-ai-and-llms-building-ai-powered-web-apps-b5c6d7780299](https://aashishkumar12376.medium.com/integrating-django-with-ai-and-llms-building-ai-powered-web-apps-b5c6d7780299)