// Create a single supabase client for interacting with your database
const supabase = window.supabase.createClient("https://aunhbyccucqlqyrempzb.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1bmhieWNjdWNxbHF5cmVtcHpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY0MzUwMDMsImV4cCI6MjA2MjAxMTAwM30.HmTblH4j0LUuI78djFix0vvLLHNZDbBpkiSJMvXAGu8");

const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const form = document.getElementById("login-form");

//註冊 & 登入
form.addEventListener("submit", async(e) => {
    e.preventDefault();
    
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // Email格式防呆
    if (!email.includes("@")|| !email.includes(".")) {
        alert("請輸入有效的 Email");
        emailInput.value = "";
        passwordInput.value = "";
        return;
    };
    
    // 先嘗試登錄 無法登錄就註冊
    // 登錄
    const { data:signInData, error:signInError } = await supabase.auth.signInWithPassword({ email, password });

    if (signInError) {
        // 登錄失敗，改為註冊
        const { data:signUpData, error:signUpError } = await supabase.auth.signUp({ email, password });
        if (signUpError) {
            alert("註冊失敗：" + signUpError.message);
            emailInput.value = "";
            passwordInput.value = "";
            return
        } else {
            alert("註冊成功！請收驗證信");
        }
    } else {
        //登錄成功，取得並儲存token
        alert("登入成功，轉跳主畫面");

        const accessToken = signInData.session.access_token;
        localStorage.setItem("access_token", accessToken);

        console.log(accessToken);

        //將access_token(jwt)包進header裡
        
        //呼叫locations API取得使用者資料

        //呼叫records API取得使用者紀錄

        //依database中的資料createElements，database中沒有的欄位也要補上渲染

    
        //都處理完後，夾帶使用者歷程，轉跳主頁面顯示table
        window.location.href = "/";
    };

});