import time,math,random,os
import utils,constants,config
import pickle, hashlib
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium import webdriver
from selenium.webdriver.common.by import By

from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException,
    ElementNotInteractableException,
    TimeoutException,
    StaleElementReferenceException
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai
import json
from difflib import SequenceMatcher
# At the top of your file, replace gemini import with:
from groq import Groq
import json
import os
import time







class Linkedin:
    def __init__(self):
        utils.prYellow("🤖 Thanks for using Easy Apply Jobs bot, for more information you can visit our site - www.automated-bots.com")
        utils.prYellow("🌐 Bot will run in Chrome browser and log in Linkedin for you.")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),options=utils.chromeBrowserOptions())
        self.cookies_path = f"{os.path.join(os.getcwd(),'cookies')}/{self.getHash(config.email)}.pkl"
        self.driver.get('https://www.linkedin.com')
        self.loadCookies()

        # Load resume
        self.resume_text = self.load_resume_text()

        # Load Q&A
        try:
            with open("additionalQuestions.json", encoding="utf-8") as f:
                self.additional_qa = json.load(f)
                print(f"✅ Loaded {len(self.additional_qa)} predefined Q&A pairs")
        except FileNotFoundError:
            print("⚠️ additionalQuestions.json not found, using AI only")
            self.additional_qa = {}
        except json.JSONDecodeError as e:
            print(f"⚠️ Invalid JSON in additionalQuestions.json: {e}")
            self.additional_qa = {}

        # ✅ REPLACE GEMINI WITH GROQ
        self.groq_client = Groq(api_key="gsk_G49BI3TK9gbLqXyb3FYJ6ok943SzoTPQVqntqC9cTwY")  # Replace with your Groq key

        # ✅ Convert Q&A to text for AI
        self.qa_text = self._convert_qa_to_text(self.additional_qa)

        # Cache for answers
        self.answer_cache = {}

        if not self.isLoggedIn():
            self.driver.get("https://www.linkedin.com/login?trk=guest_homepage-basic_nav-header-signin")
            utils.prYellow("🔄 Trying to log in Linkedin...")
            try:
                self.driver.find_element("id","username").send_keys(config.email)
                time.sleep(2)
                self.driver.find_element("id","password").send_keys(config.password)
                time.sleep(2)
                self.driver.find_element("xpath",'//button[@type="submit"]').click()
                time.sleep(30)
            except:
                utils.prRed("❌ Couldn't log in Linkedin by using Chrome. Please check your Linkedin credentials on config files line 7 and 8.")

            self.saveCookies()

        # start application
        self.linkJobApply()

    def _convert_qa_to_text(self, qa_dict):
        """Convert Q&A JSON to readable text for AI"""
        lines = []
        for section, items in qa_dict.items():
            lines.append(f"\n=== {section.upper()} ===")
            for question, answer in items.items():
                clean_answer = str(answer).strip('"\'')
                lines.append(f"Q: {question}")
                lines.append(f"A: {clean_answer}")
        return "\n".join(lines)

    def load_resume_text(self, path="resume.txt"):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    import re

    from difflib import SequenceMatcher

    def load_text_file(self,path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def parse_additional_questions(self,path="additionalQuestions.txt"):
        raw = self.load_text_file(path)
        qa_pairs = {}
        for block in raw.strip().split("\n\n"):
            lines = block.strip().split("\n")
            if len(lines) >= 2:
                question = lines[0].strip()
                answer = " ".join(lines[1:]).strip()
                qa_pairs[question] = answer
        return qa_pairs


    from difflib import SequenceMatcher
    def find_similar_question(self,user_question, qa_dict, threshold=0.6):
        """Find the most similar question using fuzzy matching"""



        # ✅ Flatten nested dictionary
        flat_qa_dict = {}
        for section in qa_dict:
            for question in qa_dict[section]:
                flat_qa_dict[question] = qa_dict[section][question]

        # ✅ Normalize helper
        def normalize(text):
            return text.lower().strip()

        user_question = normalize(user_question)
        best_match = None
        best_score = 0

        for question in flat_qa_dict:
            cleaned_q = normalize(question)

            # ✅ Substring match boost
            if user_question in cleaned_q or cleaned_q in user_question:
                score = 1.0
            else:
                # ✅ Word-level overlap score
                user_words = set(user_question.split())
                question_words = set(cleaned_q.split())
                common = user_words & question_words
                score = len(common) / max(len(user_words), len(question_words))

            if score > best_score:
                best_score = score
                best_match = question

        if best_score >= threshold:
            print(f"📌 Found match (score={best_score:.2f}): '{best_match}' → '{flat_qa_dict[best_match]}'")
            return flat_qa_dict[best_match]
        else:
            print(f"🔍 No match found for: '{user_question}' (best score: {best_score:.2f})")
            return None
        # Load cleaned JSON



    def generate_answer_with_gemini(self, question: str) -> str:
        """Generate answer using Groq AI (keeping same method name for compatibility)"""
        print(f"\n❓ Question: {question}")

        # Check cache first
        cache_key = question.lower().strip()
        if cache_key in self.answer_cache:
            print(f"✅ Using cached answer")
            return self.answer_cache[cache_key]

        # Check predefined answers with fuzzy matching
        predefined = self.find_similar_question(question, self.additional_qa)
        if predefined:
            answer = predefined.strip('"\'')
            print(f"✅ Using predefined answer: {answer}")
            return answer

        # Use Groq AI
        print("🤖 Using Groq AI...")

        prompt = f"""You are filling a job application. Use the Q&A Profile and Resume to answer.
    
    Q&A Profile (check this first for similar questions):
    {self.qa_text[:3000]}
    
    Resume:
    {self.resume_text[:2000]}
    
    Question: {question}
    
    Instructions:
    - First check if Q&A Profile has similar question, use that answer
    - If not in Q&A, generate from Resume
    - For yes/no questions: answer only "Yes" or "No"
    - For number questions: answer with number only (no units)
    - For text questions: answer in 1 short sentence maximum
    - No explanations, just the direct answer
    
    Answer:"""

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",  # Fast & accurate
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=100,
                top_p=1
            )

            raw = completion.choices[0].message.content.strip()

            # Clean response
            if self._expects_number(question):
                import re
                numbers = re.findall(r"\d+(?:\.\d+)?", raw)
                answer = numbers[0] if numbers else "0"
            elif self._expects_yes_no(question):
                answer = "Yes" if any(w in raw.lower() for w in ["yes", "true", "confirm", "i am", "i do"]) else "No"
            else:
                # Get first sentence
                answer = raw.split("\n")[0].split(".")[0].strip()
                if answer and not answer.endswith('.') and not self._expects_yes_no(question):
                    answer += "."

            # Cache it
            self.answer_cache[cache_key] = answer

            print(f"💬 Groq answer: {answer}")
            return answer

        except Exception as e:
            print(f"❌ Groq Error: {e}")
            time.sleep(1)
            return ""

    def _expects_number(self, question: str) -> bool:
        """Check if question expects a numeric answer"""
        import re
        keywords = ["how many", "number of", "years", "months", "salary", "ctc",
                    "compensation", "gpa", "percentage", "rate", "experience", "notice period"]
        return any(kw in question.lower() for kw in keywords)

    def _expects_yes_no(self, question: str) -> bool:
        """Check if question expects yes/no answer"""
        import re
        patterns = [r'^(are|is|do|does|have|has|can|could|would|will|did)']
        return any(re.search(p, question.lower()) for p in patterns)











    def choose_answer(question, options):
        # Example logic — replace with Gemini integration
        if "comfortable" in question.lower() and "Yes" in options:
            return "Yes"
        return options[0]  # fallback

    def fill_application_answers(self):

     questions =self.answer_application_questions()  # (type, question_text, element) tuples

     for q_type, question_text, input_field in questions:
        try:
            # Skip pre-filled fields (except dropdowns and radios)
            if q_type in ["text", "textarea"]:
                current_value = input_field.get_attribute("value")
                if current_value and current_value.strip() != "":
                    print(f"⏭️ Skipping pre-filled: {question_text} = {current_value}")
                    continue

            # Get answer from Gemini
            answer = self.generate_answer_with_gemini(question_text)
            if not answer or answer.strip() == "":
                print(f"⚠️ Gemini returned empty for: {question_text}")

                # Use fallback for required fields
                if q_type == "dropdown":
                    select = Select(input_field)
                    options = [opt.text.strip() for opt in select.options]
                    if len(options) > 1:
                        top_option = options[1]  # Skip "Select an option"
                        select.select_by_visible_text(top_option)
                        print(f"✅ Selected fallback '{top_option}' for {question_text}")
                elif q_type == "radio":
                    # Click first radio option as fallback
                    fieldset = input_field.find_element(By.XPATH, "./ancestor::fieldset")
                    radios = fieldset.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                    if radios:
                        radio_id = radios[0].get_attribute("id")
                        try:
                            label = fieldset.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                            self.driver.execute_script("arguments[0].click();", label)
                            print(f"✅ Selected fallback radio for {question_text}")
                        except:
                            self.driver.execute_script("arguments[0].click();", radios[0])
                continue

            # -------------------------------
            # Handle different input types
            # -------------------------------

            if q_type == "text":
                input_field.clear()
                input_field.send_keys(answer)
                print(f"📝 Filled text: {question_text} → {answer}")

            elif q_type == "textarea":
                input_field.clear()
                input_field.send_keys(answer)
                print(f"📝 Filled textarea: {question_text} → {answer}")

            elif q_type == "dropdown":
                select = Select(input_field)
                options = [opt.text.strip() for opt in select.options]

                # Try exact match first
                matched = False
                for option in options:
                    if answer.lower() == option.lower():
                        select.select_by_visible_text(option)
                        print(f"✅ Selected exact match '{option}' for {question_text}")
                        matched = True
                        break

                # Try partial match
                if not matched:
                    for option in options:
                        if answer.lower() in option.lower() or option.lower() in answer.lower():
                            select.select_by_visible_text(option)
                            print(f"✅ Selected partial match '{option}' for {question_text}")
                            matched = True
                            break

                # Fallback to first valid option
                if not matched and len(options) > 1:
                    top_option = options[1]  # Skip placeholder like "Select an option"
                    select.select_by_visible_text(top_option)
                    print(f"⚠️ No match found. Selected fallback '{top_option}' for {question_text}")

            elif q_type == "radio":
                fieldset = input_field.find_element(By.XPATH, "./ancestor::fieldset")
                radios = fieldset.find_elements(By.CSS_SELECTOR, "input[type='radio']")

                matched = False
                for radio in radios:
                    radio_id = radio.get_attribute("id")
                    radio_value = radio.get_attribute("value")

                    # Find corresponding label
                    try:
                        label = fieldset.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                        label_text = label.text.strip().lower()
                    except:
                        label = None
                        label_text = ""

                    # Check if answer matches value or label
                    answer_lower = answer.lower()
                    value_lower = radio_value.lower() if radio_value else ""

                    if (answer_lower in value_lower or value_lower in answer_lower or
                            answer_lower in label_text or label_text in answer_lower):

                        if label:
                            self.driver.execute_script("arguments[0].click();", label)
                        else:
                            self.driver.execute_script("arguments[0].click();", radio)

                        print(f"✅ Selected radio '{label_text or radio_value}' for {question_text}")
                        matched = True
                        break

                # Fallback: click first option
                if not matched and radios:
                    radio_id = radios[0].get_attribute("id")
                    try:
                        label = fieldset.find_element(By.CSS_SELECTOR, f"label[for='{radio_id}']")
                        self.driver.execute_script("arguments[0].click();", label)
                        print(f"⚠️ No match found. Selected fallback radio for {question_text}")
                    except:
                        self.driver.execute_script("arguments[0].click();", radios[0])
                        print(f"⚠️ No match found. Selected fallback radio for {question_text}")

            elif q_type == "checkbox":
                # Check if answer indicates yes/true
                if any(word in answer.lower() for word in ["yes", "true", "1", "agree", "confirm", "accept"]):
                    if not input_field.is_selected():
                        input_field.click()
                    print(f"✅ Checked: {question_text}")
                else:
                    if input_field.is_selected():
                        input_field.click()
                    print(f"✅ Unchecked: {question_text}")

            else:
                print(f"⚠️ Unsupported input type: {q_type}")

        except Exception as e:
            print(f"⚠️ Failed to fill answer for '{question_text}': {e}")
        import traceback
        traceback.print_exc()
    def answer_application_questions(self):
        import time

        try:
            questions = []

            print("🔍 Starting question extraction...")

            # Wait for form to load
            time.sleep(2)

            # -------------------
            # 1. Text input questions (with label.fb-dash-form-element__label)
            # -------------------
            try:
                labels = self.driver.find_elements(By.CSS_SELECTOR, "label.fb-dash-form-element__label")
                print(f"Found {len(labels)} labels with class 'fb-dash-form-element__label'")

                for label in labels:
                    try:
                        question_text = label.text.strip()
                        input_id = label.get_attribute("for")

                        if question_text and input_id:
                            # Try to find the input element
                            try:
                                input_field = self.driver.find_element(By.CSS_SELECTOR, f"#{input_id}")
                                tag_name = input_field.tag_name
                                input_type = input_field.get_attribute("type")

                                # Determine the type of input
                                if tag_name == "select":
                                    questions.append(("dropdown", question_text, input_field))
                                    print(f"❓ Found dropdown Q: {question_text}")
                                elif input_type in ["text", "email", "tel", "number", None]:
                                    questions.append(("text", question_text, input_field))
                                    print(f"❓ Found text input Q: {question_text}")
                                elif input_type == "radio":
                                    questions.append(("radio", question_text, input_field))
                                    print(f"❓ Found radio Q: {question_text}")
                                elif input_type == "checkbox":
                                    questions.append(("checkbox", question_text, input_field))
                                    print(f"❓ Found checkbox Q: {question_text}")
                            except Exception as e:
                                print(f"⚠️ Could not find input for '{question_text}': {e}")
                    except Exception as e:
                        print(f"⚠️ Error processing label: {e}")
            except Exception as e:
                print(f"⚠️ Error finding labels: {e}")

            # -------------------
            # 2. Radio button questions (fieldsets)
            # -------------------
            try:
                fieldsets = self.driver.find_elements(By.CSS_SELECTOR, "fieldset[data-test-form-builder-radio-button-form-component]")
                print(f"Found {len(fieldsets)} radio fieldsets")

                for fs in fieldsets:
                    try:
                        legend = fs.find_element(By.TAG_NAME, "legend")
                        question_text = legend.text.strip()

                        if question_text:
                            radios = fs.find_elements(By.CSS_SELECTOR, "input[type='radio']")
                            if radios:
                                questions.append(("radio", question_text, radios[0]))
                                print(f"❓ Found radio group Q: {question_text}")
                    except Exception as e:
                        print(f"⚠️ Error processing fieldset: {e}")
            except Exception as e:
                print(f"⚠️ Error finding fieldsets: {e}")

            # -------------------
            # 3. Additional text inputs (alternative selectors)
            # -------------------
            try:
                text_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text']:not([id*='captcha'])")
                for input_field in text_inputs:
                    input_id = input_field.get_attribute("id")
                    if input_id:
                        try:
                            # Check if we already have this input
                            if any(q[2].get_attribute("id") == input_id for q in questions):
                                continue

                            # Try to find associated label
                            label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{input_id}']")
                            question_text = label.text.strip()
                            if question_text:
                                questions.append(("text", question_text, input_field))
                                print(f"❓ Found additional text input Q: {question_text}")
                        except:
                            pass
            except Exception as e:
                print(f"⚠️ Error finding additional text inputs: {e}")

            # -------------------
            # 4. Textareas
            # -------------------
            try:
                textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
                for textarea in textareas:
                    textarea_id = textarea.get_attribute("id")
                    if textarea_id:
                        try:
                            label = self.driver.find_element(By.CSS_SELECTOR, f"label[for='{textarea_id}']")
                            question_text = label.text.strip()
                            if question_text:
                                questions.append(("textarea", question_text, textarea))
                                print(f"❓ Found textarea Q: {question_text}")
                        except:
                            pass
            except Exception as e:
                print(f"⚠️ Error finding textareas: {e}")

            if not questions:
                print("⚠️ No questions found. Trying alternative approach...")

                # Last resort: Find all data-test attributes
                try:
                    all_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-text-entity-list-form-component], [data-test-form-builder-radio-button-form-component]")
                    print(f"Found {len(all_elements)} form components as fallback")
                except:
                    pass

            print(f"✅ Total questions extracted: {len(questions)}")
            return questions

        except Exception as e:
            print(f"❌ Failed to extract questions: {e}")
            import traceback
            traceback.print_exc()
            return questions

    def getHash(self, string):
        return hashlib.md5(string.encode('utf-8')).hexdigest()

    def loadCookies(self):
        if os.path.exists(self.cookies_path):
            cookies =  pickle.load(open(self.cookies_path, "rb"))
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def saveCookies(self):
        pickle.dump(self.driver.get_cookies() , open(self.cookies_path,"wb"))

    def isLoggedIn(self):
        self.driver.get('https://www.linkedin.com/feed')
        try:
            self.driver.find_element(By.XPATH,'//*[@id="ember14"]')
            return True
        except:
            pass
        return False

    def generateUrls(self):
        if not os.path.exists('data'):
            os.makedirs('data')
        try:
            with open('data/urlData.txt', 'w',encoding="utf-8" ) as file:
                linkedinJobLinks = utils.LinkedinUrlGenerate().generateUrlLinks()
                for url in linkedinJobLinks:
                    file.write(url+ "\n")
            utils.prGreen("✅ Apply urls are created successfully, now the bot will visit those urls.")
        except:
            utils.prRed("❌ Couldn't generate urls, make sure you have editted config file line 25-39")

    def linkJobApply(self):
        self.generateUrls()
        countApplied = 0
        countJobs = 0

        urlData = utils.getUrlDataFile()

        for url in urlData:
            self.driver.get(url)
            time.sleep(random.uniform(1, constants.botSpeed))

            totalJobs = self.driver.find_element(By.XPATH,'//small').text
            totalPages = utils.jobsToPages(totalJobs)

            urlWords =  utils.urlToKeywords(url)
            lineToWrite = "\n Category: " + urlWords[0] + ", Location: " +urlWords[1] + ", Applying " +str(totalJobs)+ " jobs."
            self.displayWriteResults(lineToWrite)

            for page in range(totalPages):
                currentPageJobs = constants.jobsPerPage * page
                url = url +"&start="+ str(currentPageJobs)
                self.driver.get(url)
                time.sleep(random.uniform(1, constants.botSpeed))

                offersPerPage = self.driver.find_elements(By.XPATH, '//li[@data-occludable-job-id]')
                offerIds = [(offer.get_attribute(
                    "data-occludable-job-id").split(":")[-1]) for offer in offersPerPage]
                time.sleep(random.uniform(1, constants.botSpeed))

                for offer in offersPerPage:
                    if not self.element_exists(offer, By.XPATH, ".//*[contains(text(), 'Applied')]"):
                        offerId = offer.get_attribute("data-occludable-job-id")
                        offerIds.append(int(offerId.split(":")[-1]))

                for jobID in offerIds:
                    offerPage = 'https://www.linkedin.com/jobs/view/' + str(jobID)
                    self.driver.get(offerPage)
                    time.sleep(random.uniform(1, constants.botSpeed))

                    countJobs += 1

                    jobProperties = self.getJobProperties(countJobs)
                    if "blacklisted" in jobProperties: 
                        lineToWrite = jobProperties + " | " + "* 🤬 Blacklisted Job, skipped!: " +str(offerPage)
                        self.displayWriteResults(lineToWrite)
                    
                    else :                    
                        easyApplybutton = self.easyApplyButton()
                        time.sleep(random.uniform(1, constants.botSpeed+18))


                        if easyApplybutton is not False:
                            ii=0
                            while True and ii<7:
                             try:
                                ii+=1



                                self.fill_application_answers()
                                if self.click_button_in_shadow_dom("Next"):
                                    print("➡️ Clicked Next, moving to next step...")
                                    time.sleep(1.5)


                                # If "Next" is gone, try clicking "Submit"
                                if self.click_button_in_shadow_dom("Submit application"):
                                    print(f"✅ Application Submitted!{ii}")


                                # In some cases it's just "Review"
                                if self.click_button_in_shadow_dom("Review"):
                                    print(f"🧐 Clicked Review, continuing...{ii}")
                                    time.sleep(1.5)
                                    continue


                                time.sleep(random.uniform(1, constants.botSpeed+10))
                                lineToWrite = jobProperties + " | " + "* 🥳 Just Applied to this job: "  +str(offerPage)
                                self.displayWriteResults(lineToWrite)
                                countApplied += 1
                             except Exception:
                                 self.chooseResume()
                                 lineToWrite = jobProperties + " | " + "* 🥵 Cannot apply to this Job! " +str(offerPage)
                                 self.displayWriteResults(lineToWrite)
                                

                        else:
                            lineToWrite = jobProperties + " | " + "* 🥳 Already applied! Job: " +str(offerPage)
                            self.displayWriteResults(lineToWrite)


            utils.prYellow("Category: " + urlWords[0] + "," +urlWords[1]+ " applied: " + str(countApplied) +
                  " jobs out of " + str(countJobs) + ".")
        




    def click_button_in_shadow_dom(self, text):
        try:
            button = self.driver.execute_script(f"""
            function findButton(root) {{
                const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
                while (walker.nextNode()) {{
                    const el = walker.currentNode;
                    if (el.tagName && el.tagName.toLowerCase() === "button" &&
                        el.innerText.trim().toLowerCase() === "{text.lower()}") {{
                        return el;
                    }}
                    // Recursively search shadow roots
                    if (el.shadowRoot) {{
                        let found = findButton(el.shadowRoot);
                        if (found) return found;
                    }}
                }}
                return null;
            }}
            return findButton(document);
        """)

            if button:
                self.driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center'});
                arguments[0].dispatchEvent(new MouseEvent('mousedown', {bubbles: true}));
                arguments[0].dispatchEvent(new MouseEvent('mouseup', {bubbles: true}));
                arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));
            """, button)
                print(f"✅ Clicked button with text '{text}' using shadow-aware JS click.")
                return True
            else:
                print(f"❌ Could not find a button with text '{text}' in Shadow DOM.")
                return False

        except Exception as e:
            print(f"⚠️ Error clicking '{text}': {e}")
            return False


    #

    def chooseResume(self):
        try:
            self.driver.find_element(
                By.CLASS_NAME, "jobs-document-upload__title--is-required")
            resumes = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'ui-attachment--pdf')]")
            if (len(resumes) == 1 and resumes[0].get_attribute("aria-label") == "Select this resume"):
                resumes[0].click()
            elif (len(resumes) > 1 and resumes[config.preferredCv-1].get_attribute("aria-label") == "Select this resume"):
                resumes[config.preferredCv-1].click()
            elif (type(len(resumes)) != int):
                utils.prRed(
                    "❌ No resume has been selected please add at least one resume to your Linkedin account.")
        except:
            pass

    def getJobProperties(self, count):
        textToWrite = ""
        jobTitle = ""
        jobLocation = ""

        try:
            jobTitle = self.driver.find_element(By.XPATH, "//h1[contains(@class, 'job-title')]").get_attribute("innerHTML").strip()
            res = [blItem for blItem in config.blackListTitles if (blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobTitle += "(blacklisted title: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                utils.prYellow("⚠️ Warning in getting jobTitle: " + str(e)[0:50])
            jobTitle = ""

        try:
            time.sleep(15)
            jobDetail = self.driver.find_element(By.XPATH, "//div[contains(@class, 'job-details-jobs')]//div").text.replace("·", "|")
            res = [blItem for blItem in config.blacklistCompanies if (blItem.lower() in jobTitle.lower())]
            if (len(res) > 0):
                jobDetail += "(blacklisted company: " + ' '.join(res) + ")"
        except Exception as e:
            if (config.displayWarnings):
                print(e)
                utils.prYellow("⚠️ Warning in getting jobDetail: " + str(e)[0:100])
            jobDetail = ""

        try:
            jobWorkStatusSpans = self.driver.find_elements(By.XPATH, "//span[contains(@class,'ui-label ui-label--accent-3 text-body-small')]//span[contains(@aria-hidden,'true')]")
            for span in jobWorkStatusSpans:
                jobLocation = jobLocation + " | " + span.text

        except Exception as e:
            if (config.displayWarnings):
                print(e)
                utils.prYellow("⚠️ Warning in getting jobLocation: " + str(e)[0:100])
            jobLocation = ""

        textToWrite = str(count) + " | " + jobTitle +" | " + jobDetail + jobLocation
        return textToWrite



    def easyApplyButton(self):


        try:
            # Wait for the button to be present (not just clickable)
            button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[@id='jobs-apply-button-id' and contains(@aria-label, 'Easy Apply')]")
                )
            )

            # Bring into view (important for overlapping divs)
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", button)
            time.sleep(0.5)

            # Attempt normal click first
            try:
                button.click()
                print("✅ Clicked Easy Apply with standard Selenium click.")
                return True
            except Exception:
                # Fallback to JavaScript click if Selenium’s native click fails
                self.driver.execute_script("arguments[0].click();", button)
                print("✅ Clicked Easy Apply with JS fallback.")
                return True

        except Exception as e:
            print(f"❌ Easy Apply button not clickable: {e}")
            return False





    def applyProcess(self, percentage, offerPage):
        applyPages = math.floor(100 / percentage) - 2 
        result = ""
        for pages in range(applyPages):  
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Continue to next step']").click()

        self.driver.find_element( By.CSS_SELECTOR, "button[aria-label='Review your application']").click()
        time.sleep(random.uniform(1, constants.botSpeed))

        if config.followCompanies is False:
            try:
                self.driver.find_element(By.CSS_SELECTOR, "label[for='follow-company-checkbox']").click()
            except:
                pass

        self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Submit application']").click()
        time.sleep(random.uniform(1, constants.botSpeed))

        result = "* 🥳 Just Applied to this job: " + str(offerPage)

        return result

    def displayWriteResults(self,lineToWrite: str):
        try:
            print(lineToWrite)
            utils.writeResults(lineToWrite)
        except Exception as e:
            utils.prRed("❌ Error in DisplayWriteResults: " +str(e))

    def element_exists(self, parent, by, selector):
        return len(parent.find_elements(by, selector)) > 0

start = time.time()
kk=5
while(kk>0):
    time.sleep(12)
    Linkedin().linkJobApply()
    kk=kk-1



utils.prYellow("---Took:  minute(s).")
