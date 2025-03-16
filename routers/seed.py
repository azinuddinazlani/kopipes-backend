from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db.db_connection import get_db
from db.crud import *
from db.models.skill_assess import Skill_assess, SkillType
from db.models.employer import Employer, EmployerJobs
from typing import List
import json
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
import os
from dotenv import load_dotenv

router = APIRouter()
load_dotenv()

# Initialize LLM
llm = GoogleGenerativeAI(
    model='gemini-1.5-pro',
    temperature=0,
    api_key=os.getenv('GOOGLE_API_KEY')
)

# Create the parser and prompt template
parser = JsonOutputParser()

prompt_template = """Given the following job description, extract and organize the information into a structured JSON format.
Include the following fields:
- overview: A brief summary of the role
- requirements: Object containing technical_skills (list), soft_skills (list), experience (string), education (string), certifications (list)
- responsibilities: List of key responsibilities
- benefits: List of benefits and perks
- location: Work location/arrangement
- employment_type: Type of employment (e.g., Full-time, Part-time, Contract)

Job Description:
{description}

{format_instructions}
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["description"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

@router.post("/upload-company-info")
def upload_company_info(db: Session = Depends(get_db)):
    records = [
        {
    "name": "Gamuda Group",
    "info": "Backed by a creative and innovative workforce, Gamuda has grown since 1976 into Malaysia's leading contractor and property developer. We deliver world-class products and solutions that connect people and cities and create sustainable transformation for an enhanced quality of life. Our expertise in creating significant infrastructure and homes of the future have resulted in award-winning projects and townships and elevated industry standards. With growing national and international market presence in the Asia-Pacific region, namely Taiwan, Australia, Singapore, and Vietnam, Gamuda is poised to become a global player as we shift our focus towards sustainable townships and smart cities, digitalized construction ecosystems, and innovative building solutions in line with the rapid changes brought about by the Fourth Industrial Revolution. In addition to an inclusive and diverse workforce, we also invest in talent growth and continuous development to create an environment that nurtures an all-rounded, competitive, and self-driven workforce.",
    "logo": "https://image-service-cdn.seek.com.au/18e7d6b6668a4a0102c8cd7e9cedec836b922791",
    "job_listings": [
        {
            "name": "Executive - Credit Administration",
            "summary": "Responsible for the operations of the credit administration functions.",
            "responsibilities":
            [
                "Review and identify areas for improvement in billing and collections.",
                "Analyze and recommend enhancements to documentation processes.",
                "Monitor documentation to meet quality management system requirements.",
                "Ensure compliance with internal controls, policies, and statutory requirements.",
                "Prepare and review management reports for accuracy and timely submission.",
                "Liaise with purchasers, financial institutions, and solicitors to ensure proper documentation.",
                "Understand and improve software usage for system efficiency.",
                "Maintain accurate records of all purchasers in the developer's system."
            ],
            "qualifications": "Degree/Diploma in Administration/Management or minimum SPM.",
            "skills":
            [
                "Computer literacy",
                "Good communication and supervision skills",
                "Knowledge of property development-related statutory acts",
                "Customer-oriented approach",
                "Discipline and integrity"
            ],
            "experience": "Minimum 1-2 years of experience in credit administration or related fields.",
            "experienceyear": "1-2",
            "postedTime": "3 hours ago",
            "type": "Full-time",
            "workMode": "On-site",
            "level": "Entry"
        },
        {
            "name": "COE Specialist - English Language Unit",
            "summary": "To manage and execute an efficient training and test administration system, and to conduct training for Gamuda staff. The job requires a goal-oriented, pro-active, adaptable, and meticulous person with strong management and communication skills, and training experience.",
            "responsibilities":
            [
                "Executes the planning and implementation of an efficient test administration, and learning and development systems to upskill employees' English competence.",
                "Collaborates with all relevant parties to ensure continuous delivery of an English-competent workforce.",
                "Conducts training and develops customized training modules.",
                "Facilitates and oversees other English communication activities.",
                "Engages with all relevant parties and proactively deals with feedback to improve the English Language Unit's services.",
                "Ensures up-to-date records of test administration, course training, and performance of the target group.",
                "Assists in preparing reports in a timely and accurate manner.",
                "Undertakes any other duties as directed by the Management from time to time.",
                "Complies and adheres to all matters pertaining to Quality, Safety & Health, and Environment related to the job scope and workplace as required by the company."
            ],
            "qualifications": "A degree in B.Ed TESL or B.A. (English), and/or related Master's degree.",
            "skills":
            [
                "Problem-solving skills",
                "Attention to detail",
                "Ability to multi-task and work under pressure",
                "Course content development and testing skills",
                "Strong facilitation skills",
                "Excellent English communication skills",
                "Technology skills",
                "Report writing skills"
            ],
            "experience": "Minimum 10 years of teaching experience with relevant administrative experience.",
            "experienceyear": "10",
            "postedTime": "1 day ago",
            "type": "Contract",
            "workMode": "Hybrid",
            "level": "Mid-Senior"
        },
        {
            "name": "Executive - Administration",
            "summary": "Responsible for the smooth operation of all matters pertaining to office administration matters and assist in effective planning and management of overall office administration.",
            "responsibilities":
            [
                "Source and negotiate with contractors/suppliers for favorable contract terms.",
                "Ensure timely purchase of office equipment and maintenance of office space.",
                "Monitor and ensure payments to contractors/suppliers are processed in a timely manner.",
                "Secure office space and manage tenancy agreements.",
                "Comply and adhere to all matters related to Quality, Safety & Health, and Environment."
            ],
            "qualifications": "Degree in Business Administration or related fields.",
            "skills":
            [
                "Proficient in Microsoft Office",
                "Good communication skills",
                "Proficient in Mandarin speaking"
            ],
            "experience": "Minimum 1-2 years of relevant experience. Fresh graduates are encouraged to apply.",
            "experienceyear": "1-2",
            "postedTime": "5 days ago",
            "type": "Full-time",
            "workMode": "On-site",
            "level": "Entry"
        },
        {
            "name": "Assistant Manager - IT Application & Support",
            "summary": "Primary focus will be on IT Application Management & Support (e.g. Leisure & Hospitality, Leasing, Retail & Malls).",
            "responsibilities":
            [
                "Lead the application team in managing and supporting all existing IT applications, serving as the primary point of contact for the business.",
                "Act as a business analyst, assisting in the development and implementation of new applications and processes.",
                "Ensure seamless day-to-day operations and continuous functionality of systems.",
                "Lead and assist with the setup and configuration of pricing, promotions, and admin settings for ticketing, retail, and F&B systems such as Xilnex, Magento, and Yardi.",
                "Participate in detailed installation, configuration, and testing of IT application implementations.",
                "Liaise with service providers and vendors to troubleshoot and resolve operational issues.",
                "Maintain service uptime for all application-related services and ensure optimal efficiency and security.",
                "Manage application upgrades and patches to keep IT infrastructure up to date.",
                "Perform necessary application backup and restoration processes to meet financial and business compliance requirements.",
                "Provide alternative or backup solutions in the event of system failures.",
                "Assist during disaster recovery activation and execution.",
                "Assist in budget planning and procurement processes for IT software, applications, and services.",
                "Ensure compliance with group compliance policies and access management reviews.",
                "Perform other duties assigned by management."
            ],
            "qualifications": "Diploma / Advanced Diploma / Bachelor's Degree / Masters in IT-related qualification.",
            "skills":
            [
                "Expertise in Windows Server 2012 Enterprise, VMware, HP Data Protector (Backup & Storage), iSCSI storage technologies, Firewall security, Networking including VLAN segmentations, inter-office WAN provisioning.",
                "Knowledge of Google Cloud or similar cloud platforms for scalable IT solutions.",
                "Proficient in supporting mobile computing, laptop/desktop/POS devices including printers, office application software, and telephony services.",
                "Industry-specific experience in themed parks, ticketing, F&B, or retail environments.",
                "Familiarity with MySQL/SQL databases and corporate application systems such as ERP.",
                "Certifications such as ITIL V4, PMP, and knowledge of O365 products (Power Apps, Power BI) are highly desirable.",
                "Ability to manage and supervise IT staff effectively.",
                "Strong analytical, problem-solving, and communication skills.",
                "Ability to work independently and under pressure to meet deadlines.",
                "Willingness to travel and continuously improve technical and managerial skills."
            ],
            "experience": "At least 2-5 years of experience supporting IT environments in themed parks or similar industries.",
            "experienceyear": "2-5",
            "postedTime": "6 hours ago",
            "type": "Full-time",
            "workMode": "Hybrid",
            "level": "Mid"
        },
        {
            "name": "Manager - Insurance",
            "summary": "The Insurance Manager is responsible for managing the full lifecycle of the company's insurance portfolio to support the business's large-scale projects and serve as the primary point of contact for all insurance-related matters within the organization. This role ensures appropriate risk transfer strategies, compliance with insurance requirements, effective insurance claims management, and collaboration with stakeholders to mitigate potential financial impacts on the business. This role is to support our Australia businesses, hence the person is expected to travel and be based in Australia for a period of time.",
            "responsibilities":
            [
                "Develop and oversee insurance programs to protect the organization's assets in construction and operations.",
                "Identify insurance needs based on project and company risks, ensuring compliance with industry and regulatory standards.",
                "Collaborate with brokers and insurers to obtain competitive pricing for construction and operational insurance.",
                "Work with the Risk and Compliance team to assess risks across projects.",
                "Advise on insurance solutions and risk strategies to minimize financial impacts.",
                "Regularly review ongoing projects and adjust insurance strategies as needed.",
                "Coordinate with internal stakeholders, legal counsel, insurers, and adjusters for timely claims resolution.",
                "Maintain claim documentation and track trends to refine future strategies.",
                "Review tender insurance clauses to ensure compliance with contract and regulatory standards.",
                "Advise on insurance contract obligations and risk allocation with project teams.",
                "Ensure continuous policy compliance across all operations and projects.",
                "Train project teams on insurance requirements and claims procedures.",
                "Provide regular updates to senior management on insurance status and potential risks.",
                "Perform additional tasks as assigned by management (Gamuda HQ)."
            ],
            "qualifications": "Bachelor's degree in Finance, Business, Risk Management, or a related field. Professional certifications (e.g., ANZIIF, CIP) are advantageous.",
            "skills":
            [
                "Deep understanding of insurance policies related to construction and infrastructure.",
                "Strong analytical and negotiation skills.",
                "Excellent communication and interpersonal skills for effective stakeholder engagement.",
                "Proficiency in contract review and interpretation.",
                "Detail-oriented with strong organizational and multitasking abilities.",
                "Proactive problem-solver, collaborative, adaptable, and able to thrive in a high-paced environment."
            ],
            "experience": "At least 5-10 years experience in a similar capacity.",
            "experienceyear": "5-10",
            "postedTime": "1 day ago",
            "type": "Full-time",
            "workMode": "On-site",
            "level": "Senior",
            "location": "Australia (Requires travel and relocation)"
        },
        {
            "name": "Executive - Accounts [Fresh Graduates]",
            "summary": "Responsible for the day-to-day operational, accounting, and reporting function, and to perform monitoring on the compliance of relevant internal control procedures and to assist the Finance Manager in finance and management accounting.",
            "responsibilities":
            [
                "Responsible for the day-to-day operational matters of the accounts department.",
                "Prepare and check accounting and financial-related documents for internal reference or management's verification and approval.",
                "Prepare and review financial reports for internal and external reference and ensure timely and accurate completion.",
                "Perform monthly variance analysis on all expenses against the budget.",
                "Monitor, check, and ensure compliance with internal control procedures and accounting policies for all issued payments.",
                "Monitor bank balance, cash flow position, and fund placement.",
                "Prepare reconciliation for all balance sheet items and control accounts.",
                "Liaise with Head Office, financial institutions, auditors, and tax agents on accounting and financial matters.",
                "Assist in coordinating and preparing financial budgets, projections, and performance targets.",
                "Monitor financial performance against budgeted and projected figures, perform periodic forecasting and ad-hoc analysis.",
                "Assist in property development costing, records management, profit, and cost recognition monitoring.",
                "Provide on-job training and guidance for accounts staff.",
                "Comply with all Quality, Safety & Health, and Environmental regulations related to the job and workplace.",
                "Perform any other duties assigned by management."
            ],
            "qualifications": "Degree in Accounting, Diploma, or equivalent qualification.",
            "skills":
            [
                "Knowledge of accounting standards and internal control policies & procedures.",
                "Computer literacy.",
                "Supervisory skills."
            ],
            "experience": "No prior experience required. Fresh graduates are encouraged to apply.",
            "experienceyear": "0",
            "postedTime": "4 hours ago",
            "type": "Full-time",
            "workMode": "On-site",
            "level": "Entry"
        },
        {
            "name": "Data Protection Officer",
            "summary": "Gamuda Berhad is looking to recruit an experienced Data Protection Officer (DPO) to meet its obligations under the European Union (EU) General Data Protection Regulation (GDPR) and PDPA. Reporting to the Head of IT Governance & Compliance, the statutory DPO will monitor compliance and data practices internally across Gamuda Group to ensure the business and its functions comply with applicable requirements under GDPR, PDPA, and other related laws. The DPO will be responsible for staff training, data protection impact assessments, and internal audits. The DPO will also serve as the primary contact for supervisory authorities and individuals whose data is processed by the organization. Additional responsibilities include advising, advocating, and ensuring a sustainable and comprehensive roadmap for security and resiliency to support business demands.",
            "responsibilities":
            [
                "Implement privacy governance frameworks and manage data use in compliance with relevant laws.",
                "Develop and maintain data protection policies, processes, and tools.",
                "Review projects and conduct privacy impact assessments to ensure legal compliance.",
                "Serve as the main point of contact for employees, regulators, and authorities on data protection matters.",
                "Set global data privacy standards and ensure compliance with local regulations.",
                "Deliver privacy training to various business units and promote a culture of compliance.",
                "Conduct privacy audits and collaborate with Information Security to maintain data asset records and manage security incidents.",
                "Draft, update, and review internal data policies and guidelines.",
                "Ensure compliance with data privacy laws in IT systems and collaborate with privacy attorneys for local law advice.",
                "Assist with ISO 27001 compliance checks and provide advisory on IT and governance issues.",
                "Perform additional duties as assigned, with some domestic and international travel required."
            ],
            "qualifications": "Minimum Bachelor's Degree in Computer Science, Information Technology, Computer Engineering, Legal, or an equivalent IT-related field. Candidates holding ISACA CISA, CGEIT, ISO Lead Auditor, CRISC, CISSP, CIPT, or CIPP certifications are an added advantage.",
            "skills":
            [
                "Strong knowledge of EU data privacy and data protection regulation, with a good understanding of other major privacy frameworks and evolving legislation worldwide.",
                "Exceptional communication, problem-solving, and cross-group collaboration skills.",
                "Good command of written and spoken English.",
                "Ability to present ideas in business-friendly and user-friendly language.",
                "Ability to prioritize, track, and manage a large number of divergent tasks and action items.",
                "Ability to influence in a team-oriented, collaborative environment."
            ],
            "experience": "Minimum 3 years of relevant experience in Data Governance, Data Protection Compliance, or related fields.",
            "experienceyear": "3",
            "postedTime": "2 days ago",
            "type": "Full-time",
            "workMode": "Hybrid",
            "level": "Mid"
        },
        {
            "name": "Executive - Group Corporate Communications & Sustainability",
            "summary": "Handle Gamuda Group and Associated Companies/Projects' Communications, Branding, and Partnerships (internal and external).",
            "responsibilities":
            [
                "Support implementing strategic communications, brand, and corporate partnerships activities within the Gamuda Group Communications & Sustainability ecosystem.",
                "Assist in content development and generation for internal and external stakeholder consumption across various media channels, including social media and above/below the line.",
                "Monitor media and provide analysis of relevant news and social media chatters about the organization and industry.",
                "Support the team in crisis communication, PR campaign reporting, and management.",
                "Assist in planning and executing various events, conferences, exhibitions, town halls, and webinars (both physical and virtual).",
                "Contribute to internal change communication strategies, including content and art direction planning, execution, and campaign analysis (e.g., competitions, awareness programs, educational programs, videos).",
                "Manage the Group's Digital Archiving System and ensure all digital assets [images, videos, documents, files, etc.] are updated and filed accurately.",
                "Assist in media relations and other related assignments when required."
            ],
            "qualifications": "Bachelor of Arts - Mass Communications / Communications / Media Communication / Public Relations.",
            "skills":
            [
                "Clear and concise communication skills, proficiency in English and Bahasa Malaysia.",
                "Good writing skills, primarily in English and Bahasa Malaysia.",
                "Good grasp of numbers and basic calculations.",
                "Knowledge of the social media landscape and management.",
                "Adequate stakeholder management skills to establish, build, and maintain internal and external stakeholder relations.",
                "Ability to work laterally across different business units and geographical locations, and vertically across all staff levels.",
                "Good research, organizational, and time management skills.",
                "Excellent Microsoft Office skills.",
                "Resourceful, detail-oriented, and proactive, with the ability to manage multiple tasks/projects simultaneously while meeting deadlines."
            ],
            "experience": "One to two years of experience in public relations, marketing communications, corporate communications, branding, or content writing roles.",
            "experienceyear": "1-2",
            "postedTime": "12 hours ago",
            "type": "Full-time",
            "workMode": "Hybrid",
            "level": "Entry-Mid"
        },
        {
            "name": "Assistant Manager - Architect",
            "summary": "Responsible for product design and management scope, inclusive of product concept development and visioning, schematic design proposals, checking of detailed design, advising, and commenting on any architectural issues for product development.",
            "responsibilities":
            [
                "Analyze the development brief and prepare the overall concept plan.",
                "Develop concept visioning and theming for products and master planning.",
                "Carry out interim product testing and feasibility studies to establish clear design direction and deliverables.",
                "Work on possible concept design options for evaluation by management.",
                "Develop a robust design brief for external consultants to execute design vision.",
                "Manage external consultants' deliverables, ensuring compliance with design direction.",
                "Work on possible developed design options for evaluation by management.",
                "Ensure the design brief is prepared in accordance with development control guidelines.",
                "Liaise with consultants for layout and building plan preparation.",
                "Ensure the preparation of Planning & Building Submission aligns with the client's brief.",
                "Liaise with various departments regarding architectural-related issues.",
                "Check and monitor the design development of respective architects.",
                "Review the approved layout and building plan (if required).",
                "Design and discuss with consultants on architectural-related issues.",
                "Assist Project Management & Marketing department with architectural-related input, advice, and comments.",
                "Assist with the preparation of any Strategic Planning Materials.",
                "Provide input and advice on architectural-related matters."
            ],
            "qualifications": "Degree in Architecture.",
            "skills":
            [
                "Design skills and creativity, ability to develop and interpret ideas into a development brief.",
                "Proficiency in drafting and 3D modeling software, presentation, and graphic software.",
                "Knowledge and skills in 3D modeling, BIM, and visualization tools and software are an advantage.",
                "Demonstrate a high level of ownership and accountability for tasks undertaken.",
                "Good interpersonal skills.",
                "Ability to communicate effectively and work as part of a team with all relevant parties."
            ],
            "experience": "6 years of working experience in the architectural profession, both consultancy and developer office.",
            "experienceyear": "6",
            "postedTime": "3 days ago",
            "type": "Full-time",
            "workMode": "On-site",
            "level": "Mid-Senior"
        }
    ]
},
        {
            "name": "Google",
            "info": "Google is not a conventional company, and we don't intend to become one. True, we share attributes with the world's most successful organizations – a focus on innovation and smart business practices comes to mind – but even as we continue to grow, we're committed to retaining a small-company feel. At Google, we know that every employee has something important to say, and that every employee is integral to our success. We provide individually tailored compensation packages that can be comprised of competitive salary, bonus, and equity components, along with the opportunity to earn further financial bonuses and rewards. Googlers thrive in small, focused teams and high-energy environments, believe in the ability of technology to change the world, and are as passionate about their lives as they are about their work. At Google, we don't just accept difference - we celebrate it, we support it, and we thrive on it for the benefit of our employees, our products, and our community. Google is proud to be an equal opportunity workplace.",
            "logo": "https://image-service-cdn.seek.com.au/3a3c4de8b2850c8f6c5c3da4e2355e7136da7657",
            "job_listings": [
                {
                    "name": "Senior Software Engineer",
                    "description": "Join Google's engineering team to work on innovative projects that impact billions of users. You will design, develop, and maintain complex software systems while mentoring junior engineers."
                },
                {
                    "name": "Product Manager",
                    "description": "Lead product development from conception to launch. Work with cross-functional teams to define product strategy, roadmap, and features that delight our users."
                },
                {
                    "name": "UX Designer",
                    "description": "Create intuitive and beautiful user experiences for Google products. Work closely with product managers, engineers, and researchers to design solutions that meet user needs."
                }
            ]
        },
        {
            "name": "Popular Book Company",
            "info": "Founded in 1924, we are an established brand with a wide network and strong market share in the Malaysia retail scene. Our core businesses are in retailing, publishing, and distribution, and we are now moving into a new business segment, i.e., e-learning. Our global operations span across Singapore, Malaysia, Hong Kong, Macau, China, Taiwan, and Canada. We have maintained our competitive edge by continually striving towards better business practices and strengthening our commitment to serving our customers in the best possible way. In line with our rapid expansion needs, we are now seeking bright minds and trendsetters to join our growing team in Malaysia.",
            "logo": "https://image-service-cdn.seek.com.au/3143dd9aeddc7072f47c6c5261069721199bdcb3",
            "job_listings": [
                {
                    "name": "E-Learning Developer",
                    "description": "Help us build the future of education by developing engaging e-learning content and interactive educational platforms. Work with subject matter experts to create effective learning experiences."
                },
                {
                    "name": "Content Editor",
                    "description": "Join our editorial team to ensure high-quality educational content across our publications. Review, edit, and improve educational materials for various subjects and levels."
                },
                {
                    "name": "Digital Marketing Specialist",
                    "description": "Drive our digital marketing initiatives to promote our e-learning platforms and educational products. Develop and execute marketing strategies across digital channels."
                }
            ]
        }
    ]

    inserted_records = []
    for record in records:
        job_listings = record.pop("job_listings", [])
        
        # Check if employer already exists
        existing_employer = db.query(Employer).filter(Employer.name == record["name"]).first()
        
        if existing_employer:
            employer_id = existing_employer.id
            employer_result = existing_employer
            print(f"Company {record['name']} already exists, using existing ID: {employer_id}")
        else:
            employer_result = insert_data(db, Employer, record)
            if not employer_result:
                print(f"Failed to insert company {record['name']}")
                continue
            employer_result = db.query(Employer).filter(Employer.name == record["name"]).first()
            employer_id = employer_result.id
            print(f"Inserted new company {record['name']} with ID: {employer_id}")
            
        # Insert jobs for this employer
        for job in job_listings:
            try:
                # Use summary as description for LLM parsing
                job_description = job.get("summary", "")
                if not job_description:
                    print(f"Skipping job {job['name']} - no description/summary found")
                    continue

                # Use LLM to parse job description
                chain = prompt | llm | parser
                desc_json = chain.invoke({"description": job_description})
                
                job_data = {
                    "employer_id": employer_id,
                    "name": job["name"],
                    "description": job_description,
                    "desc_json": json.dumps(desc_json, ensure_ascii=False, indent=2),
                    "summary": job.get("summary", ""),
                    "responsibilities": json.dumps(job.get("responsibilities", []), 
                        ensure_ascii=False, 
                        indent=2,
                        separators=(',', ': ')
                    ),
                    "qualifications": job.get("qualifications", ""),
                    "skills": json.dumps(job.get("skills", []),
                        ensure_ascii=False,
                        indent=2,
                        separators=(',', ': ')
                    ),
                    "experience": job.get("experience", ""),
                    "experienceyear": job.get("experienceyear", ""),
                    "postedtime": job.get("postedTime", ""),
                    "jobtype": job.get("type", ""),
                    "workmode": job.get("workMode", ""),
                    "level": job.get("level", ""),
                    "location": job.get("location", "")
                }
                
                job_result = insert_data(db, EmployerJobs, job_data)
                if job_result:
                    job_obj = db.query(EmployerJobs).filter(
                        EmployerJobs.employer_id == employer_id,
                        EmployerJobs.name == job["name"]
                    ).first()
                    employer_result.jobs.append(job_obj)
                    print(f"Added job {job['name']} to employer {record['name']}")
            except Exception as e:
                print(f"Error processing job {job['name']}: {str(e)}")
                continue
                
        inserted_records.append(employer_result)

    return "{'ok'}"



@router.post("/modify-table")
def modify_table(db: Session = Depends(get_db)):    
    add_columns_to_table(db, "employer_jobs", {
        "summary": "TEXT",
        "responsibilities": "TEXT",
        "qualifications": "TEXT",
        "skills": "TEXT",
        "experience": "TEXT",
        "experienceyear": "TEXT",
        "postedtime": "TEXT",
        "jobtype": "TEXT",
        "workmode": "TEXT",
        "level": "TEXT",
        "location": "TEXT"
    })

    add_columns_to_table(db, "employers", {
        "location": "TEXT",
        "businessnature": "TEXT"
    })

'''


@router.post("/upload-skill-assess")
def upload_skill_assess(db: Session = Depends(get_db)):
    records = [
        {
        	"type": "Python",
          "level": "1",
          "questions": "What is the correct file extension for Python files?",
          "options": '{"A": ".py", "B": ".python", "C": ".pt", "D": ".txt"}',
          "answer": "A"
        },
        {
        	"type": "Python",
          "level": "1",
          "questions": "How do you output text in Python?",
          "options": '{"A": "print()", "B": "echo()", "C": "output()", "D": "write()"}',
          "answer": "A"
        },
        {
        	"type": "Python",
          "level": "1",
          "questions": "Which of the following is a valid variable name?",
          "options": '{"A": "1variable", "B": "variable_name", "C": "variable-name", "D": "variable.name"}',
          "answer": "B"
        },
        {
        	"type": "Python",
          "level": "1",
          "questions": "Which data type is used to store True or False values?",
          "options": '{"A": "int", "B": "float", "C": "bool", "D": "str"}',
          "answer": "C"
        },
        {
        	"type": "Python",
          "level": "1",
          "questions": "What is the output of 3 + 2 * 2?",
          "options": '{"A": "10", "B": "7", "C": "8", "D": "9"}',
          "answer": "B"
        },
        {
        	"type": "Python",
          "level": "2",
          "questions": "Which of the following loops is used to iterate over a sequence?",
          "options": '{"A": "for", "B": "while", "C": "do-while", "D": "loop"}',
          "answer": "A"
        },
        {
        	"type": "Python",
          "level": "2",
          "questions": "What is the output of the following code: 'print(2 ** 3)'?",
          "options": '{"A": "6", "B": "8", "C": "9", "D": "None of the above"}',
          "answer": "B"
        },
        {
        	"type": "Python",
          "level": "2",
          "questions": "How do you handle exceptions in Python?",
          "options": '{"A": "try...catch", "B": "try...except", "C": "try...error", "D": "try...finally"}',
          "answer": "B"
        },
        {
        	"type": "Python",
          "level": "3",
          "questions": "Which method is used to add an item to the end of a list?",
          "options": '{"A": "append()", "B": "add()", "C": "insert()", "D": "extend()"}',
          "answer": "A"
        },
        {
	"type": "Javascript",
        "level": "1",
        "questions": "What is the correct way to declare a variable in JavaScript?",
        "options": '{"A": "variable x = 5", "B": "let x = 5", "C": "x = 5", "D": "#x = 5"}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "1",
        "questions": "Which operator is used for equality comparison without type checking?",
        "options": '{"A": "===", "B": "==", "C": "=", "D": "!="}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "1",
        "questions": "How do you write a comment in JavaScript?",
        "options": '{"A": "<!-- comment -->", "B": "/* comment */", "C": "# comment", "D": "// comment"}',
        "answer": "D"
      },
      {
      	"type": "Javascript",
        "level": "1",
        "questions": "What is the correct way to write 'Hello World' in an alert box?",
        "options": '{"A": "alertBox(\"Hello World\")", "B": "msg(\"Hello World\")", "C": "alert(\"Hello World\")", "D": "msgBox(\"Hello World\")"}',
        "answer": "C"
      },
      {
      	"type": "Javascript",
        "level": "1",
        "questions": "Which method is used to add an element at the end of an array?",
        "options": '{"A": "push()", "B": "add()", "C": "append()", "D": "insert()"}',
        "answer": "A"
      },
      {
      	"type": "Javascript",
        "level": "2",
        "questions": "What is the output of: typeof([1,2,3])?",
        "options": '{"A": "\"array\"", "B": "\"object\"", "C": "\"list\"", "D": "\"number\""}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "2",
        "questions": "Which method removes the last element of an array?",
        "options": '{"A": "pop()", "B": "last()", "C": "remove()", "D": "delete()"}',
        "answer": "A"
      },
      {
      	"type": "Javascript",
        "level": "2",
        "questions": "What is the result of 3 + \"3\"?",
        "options": '{"A": "6", "B": "\"33\"", "C": "33", "D": "Error"}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "3",
        "questions": "What is the output of: [1,2,3].map(x => x*2)?",
        "options": '{"A": "[1,2,3]", "B": "[2,4,6]", "C": "undefined", "D": "Error"}',
        "answer": "B"
      },
      {
      	"type": "Javascript",
        "level": "3",
        "questions": "What is closure in JavaScript?",
        "options": '{"A": "A way to protect variables", "B": "A function with access to variables in its outer scope", "C": "A method to close browser window", "D": "A way to end loops"}',
        "answer": "B"
      }
    ]

    inserted_records = []
    for record in records:
        inserted_records.append(insert_data(db, Skill_assess, record))

    return "{'ok'}"
'''