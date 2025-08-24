# AndyLibrary User Process Flowchart

## Visual Process Flow Diagram

```mermaid
flowchart TD
    %% Start/End Nodes (Oval)
    START([Start<br/>User Opens Browser])
    END([End<br/>Book Access Complete])

    %% Process Nodes (Rectangle)
    POWER_ON[Power On<br/>Load Website]
    SCAN_ENV[Scan Environment<br/>Check Auth Status]
    GEN_MAP[Generate Map<br/>Load User Interface]
    PLAN_ROUTE[Plan Route<br/>Choose Auth Method]
    VAC_ON[Vacuum On<br/>Start Registration]
    SEND_EMAIL[Send Verification<br/>Email Process]
    LOGIN_PROCESS[Login Process<br/>Authenticate User]
    GDRIVE_SETUP[Google Drive Setup<br/>OAuth Configuration]
    FIND_FOLDER[Find Library Folder<br/>Search Google Drive]
    BOOK_SEARCH[Search Book File<br/>Locate Requested Book]

    %% Decision Nodes (Diamond)
    AUTH_CHECK{User<br/>Authenticated?}
    REG_VALID{Registration<br/>Valid?}
    EMAIL_SENT{Email<br/>Sent?}
    LOGIN_SUCCESS{Login<br/>Successful?}
    GDRIVE_AUTH{Google Drive<br/>Authorized?}
    FOLDER_EXISTS{Library Folder<br/>Exists?}
    FILE_FOUND{Book File<br/>Found?}
    BATTERY_LOW{Account<br/>Locked?}
    VACUUM_FULL{Email<br/>Verified?}
    USER_FOUND{User<br/>Found?}
    TOKEN_VALID{Token<br/>Valid?}

    %% Storage/Data Nodes (Cylinder/Database)
    ROUTE[(User Database<br/>Store User Data)]

    %% Error/Action Nodes (Parallelogram)
    RETURN_DOCK[Return to Dock<br/>Show Login Form]
    POWER_OFF[Power Off<br/>Session Expired]
    STOP_MOVING[Stop Moving<br/>Registration Failed]
    ERROR_IND[Error Indicator On<br/>Show Error Message]
    VAC_OFF_1[Vacuum Off<br/>Email Verification Failed]
    VAC_OFF_2[Vacuum Off<br/>Google Drive Failed]
    USER_NOT_FOUND[User Not Found<br/>Invalid Credentials]
    TOKEN_EXPIRED[Token Expired<br/>Request New Verification]
    DUPLICATE_USER[Duplicate User<br/>Email Already Exists]

    %% Main Flow
    START --> POWER_ON
    POWER_ON --> SCAN_ENV
    SCAN_ENV --> GEN_MAP
    GEN_MAP --> PLAN_ROUTE
    PLAN_ROUTE --> AUTH_CHECK

    %% Authentication Branch
    AUTH_CHECK -->|No| VAC_ON
    AUTH_CHECK -->|Yes| GDRIVE_SETUP

    %% Registration Flow
    VAC_ON --> REG_VALID
    REG_VALID -->|Yes| SEND_EMAIL
    REG_VALID -->|No| DUPLICATE_USER
    DUPLICATE_USER --> ERROR_IND
    STOP_MOVING --> ERROR_IND
    ERROR_IND --> PLAN_ROUTE

    %% Email Verification
    SEND_EMAIL --> EMAIL_SENT
    EMAIL_SENT -->|Yes| VACUUM_FULL
    EMAIL_SENT -->|No| VAC_OFF_1
    VAC_OFF_1 --> ERROR_IND

    VACUUM_FULL -->|Yes| TOKEN_VALID
    VACUUM_FULL -->|No| VAC_OFF_1
    TOKEN_VALID -->|Yes| LOGIN_PROCESS
    TOKEN_VALID -->|No| TOKEN_EXPIRED
    TOKEN_EXPIRED --> ERROR_IND

    %% Login Process
    LOGIN_PROCESS --> USER_FOUND
    USER_FOUND -->|Yes| BATTERY_LOW
    USER_FOUND -->|No| USER_NOT_FOUND
    USER_NOT_FOUND --> ERROR_IND
    BATTERY_LOW -->|Yes| RETURN_DOCK
    BATTERY_LOW -->|No| LOGIN_SUCCESS
    LOGIN_SUCCESS -->|Yes| ROUTE
    LOGIN_SUCCESS -->|No| RETURN_DOCK
    RETURN_DOCK --> POWER_OFF
    POWER_OFF --> END

    %% Database Storage
    ROUTE --> GDRIVE_SETUP

    %% Google Drive Setup
    GDRIVE_SETUP --> GDRIVE_AUTH
    GDRIVE_AUTH -->|Yes| FIND_FOLDER
    GDRIVE_AUTH -->|No| VAC_OFF_2
    VAC_OFF_2 --> ERROR_IND

    %% Folder and File Search
    FIND_FOLDER --> FOLDER_EXISTS
    FOLDER_EXISTS -->|Yes| BOOK_SEARCH
    FOLDER_EXISTS -->|No| VAC_OFF_2

    BOOK_SEARCH --> FILE_FOUND
    FILE_FOUND -->|Yes| END
    FILE_FOUND -->|No| VAC_OFF_2

    %% Styling
    classDef startEnd fill:#FFB6C1,stroke:#8B0000,stroke-width:3px,color:#000
    classDef process fill:#87CEEB,stroke:#000080,stroke-width:2px,color:#000
    classDef decision fill:#FFD700,stroke:#FF8C00,stroke-width:2px,color:#000
    classDef storage fill:#98FB98,stroke:#006400,stroke-width:2px,color:#000
    classDef error fill:#FFA07A,stroke:#DC143C,stroke-width:2px,color:#000
    classDef action fill:#DDA0DD,stroke:#800080,stroke-width:2px,color:#000

    class START,END startEnd
    class POWER_ON,SCAN_ENV,GEN_MAP,PLAN_ROUTE,VAC_ON,SEND_EMAIL,LOGIN_PROCESS,GDRIVE_SETUP,FIND_FOLDER,BOOK_SEARCH process
    class AUTH_CHECK,REG_VALID,EMAIL_SENT,LOGIN_SUCCESS,GDRIVE_AUTH,FOLDER_EXISTS,FILE_FOUND,BATTERY_LOW,VACUUM_FULL,USER_FOUND,TOKEN_VALID decision
    class ROUTE storage
    class STOP_MOVING,ERROR_IND,VAC_OFF_1,VAC_OFF_2,USER_NOT_FOUND,TOKEN_EXPIRED,DUPLICATE_USER error
    class RETURN_DOCK,POWER_OFF action
```

## Legend

| Shape                 | Type         | Purpose                             | Example                          |
| --------------------- | ------------ | ----------------------------------- | -------------------------------- |
| ?�� **Oval**          | Start/End    | Entry and exit points               | Start, End                       |
| ?�� **Rectangle**     | Process      | Actions and operations              | Load Website, Send Email         |
| ?�� **Diamond**       | Decision     | Yes/No choice points                | User Authenticated?, Email Sent? |
| ?�� **Cylinder**      | Storage      | Data storage                        | User Database                    |
| ?�� **Parallelogram** | Error/Action | Error states and corrective actions | Show Error, Return to Login      |

## Process Flow Explanation

### **1. Initialization Phase**

- **Start**: User opens browser
- **Power On**: Website loads
- **Scan Environment**: Check if user is already authenticated
- **Generate Map**: Load appropriate user interface
- **Plan Route**: Present authentication options

### **2. Authentication Decision**

- **Diamond Check**: Is user already authenticated?
  - **Yes**: Skip to Google Drive setup
  - **No**: Begin registration process

### **3. Registration Process**

- **Vacuum On**: Start registration form
- **Validation Check**: Is registration data valid?
  - **Yes**: Send verification email
  - **No**: Show error and return to planning

### **4. Email Verification**

- **Send Email**: Attempt email delivery
- **Email Sent Check**: Was email successfully sent?
  - **Yes**: Check if user verifies email
  - **No**: Show email error

### **5. Login Security**

- **Battery Check**: Is account locked due to failed attempts?
  - **Yes**: Return to login dock (show lockout message)
  - **No**: Process login attempt

### **6. Google Drive Integration**

- **Route Database**: Store user session data
- **Google Drive Setup**: Initialize OAuth process
- **Authorization Check**: Did user grant Google Drive access?
  - **Yes**: Search for library folder
  - **No**: Show Drive setup error

### **7. Book Access**

- **Find Folder**: Look for "AndyLibrary" folder
- **Folder Exists**: Is the folder present?
  - **Yes**: Search for specific book file
  - **No**: Show folder creation instructions

### **8. Final Delivery**

- **File Found**: Is the requested book available?
  - **Yes**: Complete success - deliver book
  - **No**: Show file upload instructions

This diagram maps directly to the AndyLibrary user journey while using the same visual conventions as your reference image, with different shapes representing different types of processes and decision points.