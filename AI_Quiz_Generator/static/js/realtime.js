// =====================================
// Real-time functionality for AI Quiz Platform
// =====================================

class RealtimeQuiz {

    constructor() {

        this.quizId = null;
        this.attemptId = null;
        this.heartbeatInterval = null;
        this.tabSwitchCount = 0;

        this.init();
    }

    // ==============================
    // INITIALIZE
    // ==============================

    init(){

        this.loadQuizInfo();
        this.setupEventListeners();
        this.startMonitoring();

    }

    // ==============================
    // LOAD QUIZ INFO FROM PAGE
    // ==============================

    loadQuizInfo(){

        const quizInput = document.querySelector('input[name="quiz_id"]');
        const attemptInput = document.querySelector('input[name="attempt_id"]');

        if(quizInput && attemptInput){

            this.quizId = quizInput.value;
            this.attemptId = attemptInput.value;

            console.log("Quiz Info Loaded:", this.quizId, this.attemptId);

        }else{

            console.warn("Quiz ID or Attempt ID not found in page.");

        }

    }

    // ==============================
    // EVENT LISTENERS
    // ==============================

    setupEventListeners(){

        this.detectTabSwitch();
        this.detectCopyPaste();
        this.detectKeyboardShortcuts();

    }

    // ==============================
    // TAB SWITCH DETECTION
    // ==============================

    detectTabSwitch(){

        document.addEventListener("visibilitychange", ()=>{

            if(document.hidden){

                // Increment tab switch counter
                this.tabSwitchCount = (this.tabSwitchCount || 0) + 1;
                
                this.reportActivity("tab_switch");

                if (this.tabSwitchCount >= 3) {
                    // Auto-submit quiz after 3 tab switches
                    this.showWarning(
                        "Tab switching limit reached! Submitting quiz automatically..."
                    );
                    
                    // Submit the quiz form
                    setTimeout(() => {
                        const quizForm = document.getElementById('quizForm');
                        if (quizForm) {
                            quizForm.dispatchEvent(new Event('submit'));
                        }
                    }, 1000);
                } else {
                    const remaining = 3 - this.tabSwitchCount;
                    this.showWarning(
                        `Tab switching detected! Please stay on the quiz page. (${remaining} attempts remaining)`
                    );
                }

            }

        });

    }

    // ==============================
    // COPY / PASTE DETECTION
    // ==============================

    detectCopyPaste(){

        document.addEventListener("copy",(e)=>{

            e.preventDefault();

            this.reportActivity("copy_attempt");

            this.showWarning("Copy is disabled during quiz.");

        });

        document.addEventListener("paste",(e)=>{

            e.preventDefault();

            this.reportActivity("paste_attempt");

            this.showWarning("Paste is disabled during quiz.");

        });

        document.addEventListener("contextmenu",(e)=>{

            e.preventDefault();

            this.reportActivity("right_click");

        });

    }

    // ==============================
    // KEYBOARD SHORTCUT DETECTION
    // ==============================

    detectKeyboardShortcuts(){

        document.addEventListener("keydown",(e)=>{

            if(

                e.key === "F12" ||
                (e.ctrlKey && e.shiftKey && e.key === "I") ||
                (e.ctrlKey && e.key === "U") ||
                (e.ctrlKey && e.key === "S")

            ){

                e.preventDefault();

                this.reportActivity("suspicious_key");

                this.showWarning(
                    "Developer shortcuts are disabled during quiz."
                );

            }

        });

    }

    // ==============================
    // ACTIVITY REPORT
    // ==============================

    reportActivity(type){

        if(!this.quizId || !this.attemptId){

            console.warn("Activity skipped: Missing quiz info.");
            return;

        }

        const activity = {

            type:type,
            quizId:this.quizId,
            attemptId:this.attemptId,
            time:new Date().toISOString()

        };

        fetch("/report_activity",{

            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify(activity)

        })
        .then(res=>res.json())
        .then(data=>{
            console.log("Activity logged:",data);
        })
        .catch(err=>{
            console.log("Activity report failed");
        });

    }

    // ==============================
    // WARNING MESSAGE
    // ==============================

    showWarning(message){

        const alertContainer = document.getElementById("alertContainer");

        if(!alertContainer) return;

        const alert = document.createElement("div");

        alert.className="alert alert-warning";

        alert.innerHTML=`
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
        `;

        alertContainer.appendChild(alert);

        setTimeout(()=>{

            alert.remove();

        },4000);

    }

    // ==============================
    // MONITORING
    // ==============================

    startMonitoring(){

        this.heartbeatInterval = setInterval(()=>{

            this.sendHeartbeat();

        },30000);

        this.detectDevTools();

    }

    // ==============================
    // HEARTBEAT
    // ==============================

    sendHeartbeat(){

        fetch("/heartbeat",{

            method:"POST"

        }).catch(()=>{

            console.log("Heartbeat failed");

        });

    }

    // ==============================
    // DEVTOOLS DETECTION
    // ==============================

    detectDevTools(){

        const threshold = 160;

        setInterval(()=>{

            if(

                window.outerWidth - window.innerWidth > threshold ||
                window.outerHeight - window.innerHeight > threshold

            ){

                this.reportActivity("devtools_open");

                this.showWarning(
                    "Developer tools detected."
                );

            }

        },2000);

    }

}

// ==============================
// INITIALIZE SCRIPT
// ==============================

document.addEventListener("DOMContentLoaded",()=>{

    window.realtimeQuiz = new RealtimeQuiz();

});