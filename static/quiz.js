function checkAnswers() {
    const q1 = document.querySelector('input[name="q1"]:checked');
    const q2 = document.querySelector('input[name="q2"]:checked');
    const q3 = document.querySelector('input[name="q3"]:checked');
    if (!q1 || !q2 || !q3) { alert("Please answer all questions!"); return; }
    let score = 0;
    if (q1.value === "correct") score++;
    if (q2.value === "correct") score++;
    if (q3.value === "correct") score++;
    const result = document.getElementById("result");
    result.style.display = "block";
    const emoji = score === 3 ? "🎉" : score >= 2 ? "👍" : "📖";
    const msg   = score === 3 ? "Perfect score!" : score >= 2 ? "Almost there!" : "Keep studying!";
    result.innerHTML = `${emoji} Your Score: <strong>${score} / 3</strong> — ${msg}`;
    if (score === 3) { result.style.background="rgba(52,211,153,0.1)"; result.style.borderColor="rgba(52,211,153,0.3)"; result.style.color="#34d399"; }
    else if (score >= 2) { result.style.background="rgba(251,191,36,0.1)"; result.style.borderColor="rgba(251,191,36,0.3)"; result.style.color="#fbbf24"; }
    else { result.style.background="rgba(248,113,113,0.1)"; result.style.borderColor="rgba(248,113,113,0.3)"; result.style.color="#f87171"; }
    result.scrollIntoView({ behavior: "smooth", block: "nearest" });
}
