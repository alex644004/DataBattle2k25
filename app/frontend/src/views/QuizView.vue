<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();

const questions = ref([]);
const currentIndex = ref(0);
const userAnswers = ref([]);
const userJustifications = ref([]);
const selectedOption = ref("");
const showCorrection = ref(false);

onMounted(() => {
  const storedQuestions = sessionStorage.getItem("questions");
  if (storedQuestions) {
    questions.value = JSON.parse(storedQuestions);
    console.log("Source de la question actuelle:", questions.value[currentIndex.value].Sources);
  } else {
    console.error("Aucune question trouvée !");
  }
});

const generatedExplanation = ref(""); // Stocker l'explication

const validateAnswer = async () => {
  if (selectedOption.value === "") return;

  const currentQuestion = questions.value[currentIndex.value];

  const requestData = {
    student_answer: userJustifications.value[currentIndex.value] || "",
    expected_answer: currentQuestion.Explanation
  };

  try {
    const response = await axios.post("http://127.0.0.1:5000/api/evaluate_justification", requestData, {
      headers: { "Content-Type": "application/json" }
    });

    const justificationEvaluation = response.data.final_decision; // true ou false
    let isCorrect = selectedOption.value === currentQuestion.CorrectAnswer && justificationEvaluation;
    let justificationEvaluationResult = false;

    // Si la réponse est fausse, on n'évalue PAS la justification
    if (justificationEvaluation) {
      justificationEvaluationResult = true; // On évalue normalement
    } else {
      justificationEvaluationResult = false; // On ignore l'évaluation
    }

    if (!justificationEvaluation) {
      await fetchExplanation(currentQuestion.QuestionText, currentQuestion.Explanation, userJustifications.value[currentIndex.value] || "");
    }

    userAnswers.value[currentIndex.value] = {
      question: currentQuestion.QuestionText,
      options: currentQuestion.Options,
      selected: selectedOption.value,
      correct: isCorrect,
      justification: userJustifications.value[currentIndex.value] || "",
      correctAnswer: currentQuestion.CorrectAnswer,
      explanation: currentQuestion.Explanation,
      justificationCorrect: justificationEvaluation,
      generatedExplanation: generatedExplanation.value,
      source: currentQuestion.Sources
    };


    showCorrection.value = true;
  } catch (error) {
    console.error("Erreur lors de l'évaluation :", error);
  }
};

const fetchExplanation = async (question, expectedAnswer, studentAnswer) => {
  try {
    const response = await axios.post("http://127.0.0.1:5000/api/explain_answer", {
      question: question,
      expected_answer: expectedAnswer,
      student_answer: studentAnswer
    });

    generatedExplanation.value = response.data.explanation;
  } catch (error) {
    console.error("Erreur lors de la récupération de l'explication :", error);
    generatedExplanation.value = "Une erreur est survenue lors de la génération de l'explication.";
  }
};




const nextQuestion = () => {
  selectedOption.value = "";
  showCorrection.value = false; // Cacher la correction
  currentIndex.value++;

  if (currentIndex.value >= questions.value.length) {
    // 🔹 Stocker les réponses en sessionStorage
    sessionStorage.setItem("userAnswers", JSON.stringify(userAnswers.value));

    // 🔹 Rediriger vers la page de récapitulatif
    router.push({ name: "Recap" });
  }
};


</script>

<template>
  <div class="background">
    <div class="container">
      <div v-if="questions.length > 0 && currentIndex < questions.length">
        <h1>Question {{ currentIndex + 1 }} / {{ questions.length }}</h1>

        <div class="questionsss">
          <p class="question-text">{{ questions[currentIndex].QuestionText }}</p>
          <div class="options">
            <label v-for="(option, key) in questions[currentIndex].Options" :key="key" class="option-label" :class="{
              'radio-correct': showCorrection && key === userAnswers[currentIndex].correctAnswer,
              'radio-wrong': showCorrection && key === selectedOption && key !== userAnswers[currentIndex].correctAnswer
            }">
              <input type="radio" v-model="selectedOption" :value="key" :disabled="showCorrection" />
              {{ key }}. {{ option }}
            </label>
          </div>
        </div>

        <!-- ✅ Formulaire de justification (affiché uniquement si pas encore corrigé) -->
        <div class="bottom-section" v-if="!showCorrection">
          <textarea v-model="userJustifications[currentIndex]" placeholder="Justify your answer here..."
            class="justification-box"></textarea>
          <button @click="validateAnswer" class="validate-btn">Valider</button>
        </div>

        <!-- ✅ Section Correction -->
        <div v-if="showCorrection" class="bottom-section">
          <div class="explanation-box">
            <p v-if="userAnswers[currentIndex].correct" class="correct-answer">
              ✅ Your answer is correct !
            </p>

            <p v-if="userAnswers[currentIndex].correct">
              <strong>Your answer :</strong> {{ userAnswers[currentIndex].justification }}
            </p>

            <div v-else>
              <p class="wrong-answer">
                ❌ Your answer is incorrect, Here is an explanation:
              </p>

              <p v-if="!userAnswers[currentIndex].correct && userAnswers[currentIndex].justificationCorrect">
                <strong>You got the right justification but you answered wrong to the question. Your answer : </strong>
              </p>
              <p v-if="!userAnswers[currentIndex].correct && userAnswers[currentIndex].justificationCorrect">
                {{ userAnswers[currentIndex].justification }}
              </p>
              <p v-else class="explanation">
                {{ generatedExplanation }}
              </p>
            </div>

            <!-- ✅ Ajout de la source si elle existe -->
            <div v-if="questions[currentIndex].Sources" class="source-box">
              📚 <strong>Where to revise for this question :</strong>
              <p>
                <strong>File :</strong> {{ questions[currentIndex].Sources.original_filename }} <br>
                <strong>Section :</strong> {{ questions[currentIndex].Sources.section }} <br>
                <strong>Title :</strong> {{ questions[currentIndex].Sources.title }}
              </p>
            </div>
          </div>

          <!-- ✅ Bouton "Next" correctement placé -->
          <button @click="nextQuestion" class="next-btn">Next</button>
        </div>
      </div>

      <!-- ✅ Message quand les questions chargent -->
      <div v-else>
        <p>Chargement des questions...</p>
      </div>

    </div>
  </div>
</template>

<style scoped>
.container {
  text-align: center;
  padding: 20px;
  max-width: 75%;
  margin: auto;
  display: flex;
  flex-direction: column;
  align-items: center;

}

.questionsss {
  /* width: 100%; */
  min-height: 27em;
  /* Hauteur minimum pour toutes les questions */
  display: flex;
  flex-direction: column;
  justify-content: normal;
  padding-top: 10px;
  padding-bottom: 20px;
  padding-left: 20px;
  padding-right: 40px;
  /* padding: 30px; */
  border-radius: 20px;
  background: white;
}

.question-text {
  font-size: 1.4rem;
  text-align: justify;
}

.options {
  display: flex;
  flex-direction: column;
  align-items: start;
}

.option-label {
  margin: 10px 0;
  text-align: justify;
  font-size: 1.3rem;
}

.bottom-section {
  width: 100%;
  display: flex;
  align-items: stretch;
  /* Étire les éléments pour qu'ils aient la même hauteur */
  justify-content: space-between;
  gap: 3rem;
  /* Ajoute un espace entre la textarea et le bouton */
  margin-top: 20px;
}

.justification-box {
  /* flex: 1; Permet à la textarea de prendre tout l’espace disponible */
  width: 75%;
  height: 8em;
  padding: 8px;
  box-sizing: border-box;
  font-size: 1.2rem;
  border-radius: 10px;
  resize: none;
  border: none;
}

.validate-btn {
  /* width: 14rem;
  height: 8em; Assure que la hauteur du bouton est la même que la textarea */
  background: #5c6379;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 10px;
  font-size: 1.5em;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Centre le texte à l'intérieur du bouton */
  white-space: nowrap;
  /* Évite que le texte ne se coupe */
  width: 10em;
}


.correction-box {
  margin-top: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  text-align: left;
  font-size: 1.3rem;

}

.correct-answer {
  color: green;
  font-weight: bold;
}

.wrong-answer {
  color: red;
  font-weight: bold;
}

.next-btn {
  background: #5c6379;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 10px;
  font-size: 1.5em;
  display: flex;
  align-items: center;
  justify-content: center;
  /* Centre le texte à l'intérieur du bouton */
  white-space: nowrap;
  /* Évite que le texte ne se coupe */
  width: 10em;
  height: 8em;

}

.radio-correct label {
  color: green;
}

.radio-wrong label {
  color: red;
}

.radio-correct {
  color: green;
}

.radio-wrong {
  color: red;
}

:global(body) {
  background-color: #dfdddc;
}

h1 {
  color: #30343F;
  font-size: 2.5em;
}

.explanation-box {
  width: 100%;

  display: flex;
  flex-direction: column;
  justify-content: normal;
  padding-top: 10px;
  padding-bottom: 20px;
  padding-left: 20px;
  padding-right: 30px;
  border-radius: 20px;
  background: white;
  text-align: justify;
  font-size: 1.3rem;
}
</style>
