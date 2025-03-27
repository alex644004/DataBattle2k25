<script setup>
import { ref, onMounted } from "vue";

const userAnswers = ref([]);
const score = ref(0);
const totalQuestions = ref(0);
const selectedIndex = ref(null);

onMounted(() => {
  const storedAnswers = sessionStorage.getItem("userAnswers");
  if (storedAnswers) {
    userAnswers.value = JSON.parse(storedAnswers);

    totalQuestions.value = userAnswers.value.length;
    console.log("Réponses de l'utilisateur:", userAnswers.value);

    score.value = userAnswers.value.filter(answer => answer.correct).length;
  }
});
const selectQuestion = (index) => {
  selectedIndex.value = selectedIndex.value === index ? null : index; // Active/Désactive l'affichage
};
</script>

<template>
  <div class="container">
    <h1>Récapitulatif du Quiz</h1>

    <div class="score-box">
      <h2>Votre score : {{ score }} / {{ totalQuestions }}</h2>
    </div>

    <!-- Navigation entre les questions -->
    <div class="question-nav">
      <button v-for="(answer, index) in userAnswers" :key="index" @click="selectQuestion(index)" :class="{
        'correct-btn': answer.correct,
        'incorrect-btn': !answer.correct
      }">
        {{ index + 1 }}
      </button>
    </div>

    <!-- Vérification avant d'afficher -->
    <div v-if="selectedIndex !== null && userAnswers[selectedIndex]" class="recap-item">
      
      <h2>Question {{ selectedIndex + 1 }}</h2>
      <p :class="userAnswers[selectedIndex].correct ? 'correct' : 'incorrect'">
        {{ userAnswers[selectedIndex].correct ? "✅ Correct answer" : "❌ Incorrect answer" }}
      </p>
      <p><strong>Question:</strong> {{ userAnswers[selectedIndex].question }}</p>
      <p><strong>Options:</strong></p>
      <ul>
        <p v-for="(optionText, optionKey) in userAnswers[selectedIndex].options" :key="optionKey" :class="{
          'correct': userAnswers[selectedIndex].correctAnswer === optionKey,
          'incorrect': userAnswers[selectedIndex].selected === optionKey && userAnswers[selectedIndex].correctAnswer !== optionKey
        }">
          <strong>{{ optionKey }}.</strong> {{ optionText }}
        </p>

      </ul>
      <p><strong>Your justification:</strong> {{ userAnswers[selectedIndex].justification }}</p>
      <p><strong>Was your justification correct?</strong> {{ userAnswers[selectedIndex].justificationCorrect ? "✅ Yes" :
        "❌ No" }}</p>
      <p v-if="userAnswers[selectedIndex].generatedExplanation">
        <strong>Explanation:</strong> {{ userAnswers[selectedIndex].generatedExplanation }}
      </p>

      <div v-if="userAnswers[selectedIndex].source" class="source-box">
        <p>📚 <strong>Where to revise for this question :</strong></p>
        <p>
          <strong>File :</strong> {{ userAnswers[selectedIndex].source.original_filename }} <br>
          <strong>Section :</strong> {{ userAnswers[selectedIndex].source.section }} <br>
          <strong>Title :</strong> {{ userAnswers[selectedIndex].source.title }}
        </p>
      </div>

    </div>
  </div>
</template>

<style scoped>
.container {
  text-align: center;
  padding: 20px;
}

.score-box {
  background: #5c6379;
  color: white;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 10px;
  font-size: 1.5em;
  font-weight: bold;
}

/* Style de la navigation */
.question-nav {
  margin: 20px 0;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.question-nav button {
  width: 1.5em;
  height: 1.5em;
  font-size: 3.2rem;
  font-weight: bold;
  border: none;
  border-radius: 24%;
  cursor: pointer;
  transition: 0.3s;
}

.correct-btn {
  background-color: rgba(0, 128, 0, 0.53);
  color: white;
}

.incorrect-btn {
  background-color: #ff00008a;
  color: white;
}

.recap-item {
  background: white;
  padding: 15px;
  margin: 10px 0;
  border-radius: 8px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  text-align: left;
}

.correct {
  color: green;
  font-weight: bold;
}

.incorrect {
  color: red;
  font-weight: bold;
}
</style>