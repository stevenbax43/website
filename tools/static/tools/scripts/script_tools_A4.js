document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("question-form");
    const answerInput = document.getElementById("answer-input");
    const cards = document.querySelectorAll(".option-card");

    if (!form || !answerInput || !cards.length) {
        return;
    }
    let isSubmitting = false;
    cards.forEach(card => {

        card.addEventListener("click", () => {
            
            if (isSubmitting) {
                return;
            }

            isSubmitting = true;
            
            cards.forEach(c => {
                c.classList.remove("selected");
            });

            card.classList.add("selected");

            answerInput.value = card.dataset.value;

            setTimeout(() => {
                form.submit();
            }, 150);

        });

    });

});
