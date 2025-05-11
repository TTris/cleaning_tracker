// Create a single supabase client for interacting with your database
const supabase = window.supabase.createClient("https://aunhbyccucqlqyrempzb.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImF1bmhieWNjdWNxbHF5cmVtcHpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDY0MzUwMDMsImV4cCI6MjA2MjAxMTAwM30.HmTblH4j0LUuI78djFix0vvLLHNZDbBpkiSJMvXAGu8");

//註冊 & 登入
const form = document.getElementById("login-form");
if (form) {
    form.addEventListener("submit", async(e) => {
        e.preventDefault();
        
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value;

        // Email格式防呆
        if (!email.includes("@")|| !email.includes(".")) {
            alert("請輸入有效的 Email");
            document.getElementById("email").value = "";
            document.getElementById("password").value = "";
            return;
        };
        
        // 先嘗試登錄 無法登錄就註冊
        try {
            // login
            const { data:signInData, error:signInError } = await supabase.auth.signInWithPassword({ email, password });
            if (signInData?.session) {
                // login successful, store access_token
                const accessToken = signInData?.session?.access_token;
                localStorage.setItem("access_token", accessToken);
                alert("登入成功，轉跳主畫面");
                window.location.href = "/";
                return;
            }

            // login failed, try signUp
            if (signInError?.message.includes("Invalid login credentials")) {
                const { data:signUpData , error:signUpError } = await supabase.auth.signUp({ email, password});
                
                if (signUpError) {
                    if (signUpError.code === "weak_password") {
                        alert("密碼至少需輸入6字元");
                    } else {
                        alert("註冊失敗：" + signUpError.message);
                    }
                    return;
                }
                if (signUpData && signUpData.user) {
                    // if length of data.identities = 0, user exist
                    if (signUpData.user.identities.length===0) {
                        alert("此帳號已存在，請輸入正確密碼");
                        document.getElementById("password").value = ""
                    } else {
                        alert("註冊成功！請至信箱收驗證信");
                    }
                }
            } else {
                alert("登入失敗：" + signInError.message);
            }
        } catch (error) {
            console.error(error);
            alert("發生未知錯誤，請稍後再試");
        }
    });


    // 忘記密碼
    document.getElementById("forget-pw-btn")?.addEventListener("click", async() => {
        const email = document.getElementById("email").value.trim();

        // Email防呆
        if (!email) {
            alert("請輸入Email");
            document.getElementById("email").value = "";
            document.getElementById("password").value = "";
            return;
        }
        if (!email.includes("@")|| !email.includes(".")) {
            alert("請輸入有效的 Email");
            document.getElementById("email").value = "";
            document.getElementById("password").value = "";
            return;
        }
        const { data, error } = await supabase.auth.resetPasswordForEmail(email);
        if (error) {
            alert("發送失敗：" + error.message);
        } else {
            alert("請至信箱查收重設密碼");
        }
    });
}



// 首頁表格邏輯&取得後端資料
async function loadAndRenderCleaningTable() {
    const spinner = document.getElementById("loading-spinner");
    const tableContainer = document.getElementById("cleaning-table-container");
    const loginLink = document.getElementById("login-link");
    const logoutBtn = document.getElementById("logout-btn");

    spinner.style.display = "none";
    tableContainer.innerHTML = "";   // 清空舊表格

    const accessToken = localStorage.getItem("access_token");

    if (!accessToken) {
        if (loginLink) loginLink.style.display = "block";
        if (logoutBtn) logoutBtn.style.display = "none";
        return;
    }

    if (loginLink) loginLink.style.display = "none";
    if (logoutBtn) logoutBtn.style.display = "block";

    spinner.style.display = "block";

    try {
      const [resLoc, resRec] = await Promise.all([
        fetch("/api/locations", {
          headers: { "Authorization": `Bearer ${accessToken}` }
        }),
        fetch("/api/records", {
          headers: { "Authorization": `Bearer ${accessToken}` }
        })
      ]);
  
      const locations = await resLoc.json();
      const records = await resRec.json();
  
      renderCleaningTable(locations, records, accessToken);

    } catch (e) {
      alert("資料載入失敗：" + e.message);

    } finally {
      spinner.style.display = "none"; // 載入結束
    }
  }
  
  // 渲染表格
  function renderCleaningTable(locations, records, accessToken) {
    const container = document.getElementById("cleaning-table-container");
    container.innerHTML = "";
  
    const today = new Date();
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - 14); // 前兩週
    const endDate = new Date(today);
    endDate.setDate(today.getDate() + 7); // 下一週

    const dateRange = [];
    let current = new Date(startDate);
    while (current <= endDate) {
        dateRange.push(new Date(current)); 
        current.setDate(current.getDate() + 1); 
    }
  
    const recordMap = {};
    records.forEach(rec => {
        if (rec.cleaned) {
            if (!recordMap[rec.location_id]) recordMap[rec.location_id] = new Set();
            recordMap[rec.location_id].add(rec.date);
          }
        });
  
    const table = document.createElement("table");
    table.classList.add("cleaning-table");
  
    // 月份列
    const monthRow = document.createElement("tr");
    monthRow.innerHTML = "<th></th>";
    let currentMonth = "";
    let spanCount = 0;
    let monthCell = null;
  
    dateRange.forEach((date, idx) => {
      const month = date.getMonth() + 1;
      if (month !== currentMonth) {
        if (monthCell) monthCell.colSpan = spanCount;
        monthCell = document.createElement("th");
        monthCell.innerText = `${month}月`;
        monthRow.appendChild(monthCell);
        currentMonth = month;
        spanCount = 1;
      } else {
        spanCount++;
      }
      if (idx === dateRange.length - 1 && monthCell) {
        monthCell.colSpan = spanCount;
      }
    });
    table.appendChild(monthRow);
  
    // 日期列
    const weekName = ["日", "一", "二", "三", "四", "五", "六"];
    const dateRow = document.createElement("tr");
    dateRow.innerHTML = "<th>地點</th>";

    dateRange.forEach((date) => {
        const th = document.createElement("th");
        const day = date.getDate();
        const weekDay = weekName[date.getDay()];

        th.innerText = `${day}(${weekDay})`;
        
        // mark today
        const today = new Date();
        if (
            date.getFullYear() === today.getFullYear() &&
            date.getMonth() === today.getMonth() &&
            date.getDate() === today.getDate()
        ) {
            th.classList.add("today");
        }

        if (date.getDay() === 0 || date.getDay() === 6) {  // ✅ 判斷星期六日
            th.classList.add("weekend");
        }
        dateRow.appendChild(th);
    });
    table.appendChild(dateRow);
  
    // 地點 x 日期列
    locations.forEach(loc => {
        const tr = document.createElement("tr");
        const nameTd = document.createElement("td");

        const nameSpan = document.createElement("span");
        nameSpan.innerText = loc.name;
        nameSpan.style.marginRight = "5px";

        const editBtn = document.createElement("button");
        editBtn.innerText = "✏️";
        editBtn.classList.add("edit-btn");

        const trashBtn = document.createElement("button");
        trashBtn.innerText = "🗑️";
        trashBtn.classList.add("trash-btn");

        // edit location name
        editBtn.addEventListener("click", () => {
            const input = document.createElement("input");
            input.type = "text";
            input.value = loc.name;
            input.classList.add("edit-location-input");

            const confirmBtn = document.createElement("button");
            confirmBtn.innerText = "✅";
            confirmBtn.classList.add("confirm-btn");

            nameTd.innerHTML = "";
            nameTd.appendChild(input);
            nameTd.appendChild(confirmBtn);

            confirmBtn.addEventListener("click", async() => {
                const newName = input.value.trim();
                if (newName && newName !== loc.name) {
                    await fetch (`/api/locations/${loc.id}`, {
                        method : "PATCH",
                        headers : {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${accessToken}`
                        },
                        body: JSON.stringify({name: newName})
                    });
                    loadAndRenderCleaningTable();
                } else {
                    loadAndRenderCleaningTable();
                }
            });
            input.addEventListener("keydown", async (e) => {
                if (e.key === "Enter") {
                    confirmBtn.click();
                }
            });
        });


        //delete location
        trashBtn.addEventListener("click", async() => {
            if (confirm(`確定要刪除「${loc.name}」嗎？`)){
                await fetch(`/api/locations/${loc.id}`, {
                    method: "DELETE",
                    headers: { Authorization: `Bearer ${accessToken}`}
                });
                loadAndRenderCleaningTable();
            }
        });

        nameTd.appendChild(nameSpan);
        nameTd.appendChild(editBtn);
        nameTd.appendChild(trashBtn);
        tr.appendChild(nameTd);
    
        dateRange.forEach(date => {
            const dateStr = date.toISOString().split("T")[0];
            const td = document.createElement("td");
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
    
            if (recordMap[loc.id] && recordMap[loc.id].has(dateStr)) {
                checkbox.checked = true;
            }

            // mark today
            if (
                date.getFullYear() === today.getFullYear() &&
                date.getMonth() === today.getMonth() &&
                date.getDate() === today.getDate()
            ) {
                td.classList.add("today");
            }
    
            checkbox.addEventListener("change", async () => {
                const cleaned = checkbox.checked;
                const payload = {
                    location_id: loc.id,
                    date: dateStr,
                    cleaned
            };
    
                const res = await fetch("/api/records", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "Authorization": `Bearer ${accessToken}`
                    },
                    body: JSON.stringify(payload)
                });
        
                if (!res.ok) {
                    alert("⚠️ 更新失敗");
                    checkbox.checked = !cleaned;
                }
                });

            if (date.getDay()===0 || date.getDay()===6) {
                td.classList.add("weekend");
            }
        
            td.appendChild(checkbox);
            tr.appendChild(td);
        });
    
        table.appendChild(tr);
    });

    //新增地點
    const addTr = document.createElement("tr");
    const addTd = document.createElement("td");
    addTd.colSpan = dateRange.length + 1;
    const input = document.createElement("input");
    input.placeholder = "➕新增地點";
    input.classList.add("add-location-input");

    input.addEventListener("keydown", async(e) => {
        if (e.key === "Enter" && input.value.trim()) {
            await createLocation(input.value.trim(), accessToken);
            input.value = "";
            loadAndRenderCleaningTable();
        }
    });

    const addBtn = document.createElement("button");
    addBtn.innerText = "➕";
    addBtn.addEventListener("click", async() => {
        if (input.value.trim()) {
            await createLocation(input.value.trim(), accessToken);
            input = "";
            loadAndRenderCleaningTable();
        }
    });
    
    addTd.appendChild(input);
    addTd.appendChild(addBtn);
    addTr.appendChild(addTd);
    table.appendChild(addTr);

    container.appendChild(table);
  }

// 新增地點function
async function createLocation(name, accessToken) {
    await fetch("/api/locations", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${accessToken}`
        },
        body: JSON.stringify({name})
    });
}

// 登出按鈕
const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
        localStorage.removeItem("access_token");
        window.location.href = "/login";
    });
}

// check if localstorage accessToken has expired
function isTokenExpired(token) {
    if (!token) return true;

    try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        const exp = payload.exp;
        const now = Math.floor(Date.now() / 1000); //down to second

        return exp < now;
    } catch (e) {
        return true; // wrong token format
    }
}

// for forget password
const resetPasswordBtn = document.getElementById("update-password-btn")
if (resetPasswordBtn) {
    resetPasswordBtn.addEventListener("click", async () => {
        const newPassword = document.getElementById("new-password").value.trim();
        if (!newPassword) {
        alert("請輸入新密碼");
        return;
        }
        const { data, error } = await supabase.auth.updateUser({ password: newPassword });
        if (error) {
        alert("密碼更新失敗：" + error.message);
        } else {
        alert("密碼更新成功，請重新登入！");
        localStorage.removeItem("access_token");
        window.location.href = "/login";
        }
    });
}

// 自動渲染邏輯
window.addEventListener("DOMContentLoaded", async () => {
    const hashParams = new URLSearchParams(window.location.hash.substring(1)); 
    const accessToken = hashParams.get("access_token");
    const type = hashParams.get("type");

    // for forget password
    if (accessToken && type === "recovery") {
        try {
            const { data, error } = await supabase.auth.setSession({ access_token: accessToken, refresh_token: accessToken });
            if (error) {
                console.error("Exchange session failed", error.message);
                alert("登入失敗，請重新操作重設密碼");
                window.location.href = "/login";
                return;
            }
            localStorage.setItem("access_token", data.session.access_token);
            alert("請設定新密碼");
            window.location.href = "/reset-password";
            return; 
        } catch (e) {
            console.error("Exchange session failed", e);
            alert("發生錯誤，請重新操作重設密碼");
            window.location.href = "/login";
            return;
        }
    }

    const path = window.location.pathname;
    if (path === "/") {
        const localToken = localStorage.getItem("access_token");
        if (!localToken || isTokenExpired(localToken)) {
            alert("登入逾期，請重新登入");
            localStorage.removeItem("access_token");
            window.location.href = "/login";
            return;
        }
        loadAndRenderCleaningTable();
    }
});