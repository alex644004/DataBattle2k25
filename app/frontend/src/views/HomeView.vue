<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";

const router = useRouter();
const themes = ref([]);

const fetchThemes = async () => {
  try {
    const response = await axios.get("http://127.0.0.1:5000/api/themes");
    themes.value = response.data;
  } catch (error) {
    console.error("Erreur lors du chargement des thèmes :", error);
  }
};

const goToQuiz = async (subtheme) => {
  try {
    console.log("Envoi du sous-thème :", subtheme);

    const res = await axios.post("http://127.0.0.1:5000/api/questions", {
      theme: subtheme,
    });

    console.log("Questions reçues :", res.data);

    sessionStorage.setItem("questions", JSON.stringify(res.data));

    router.push(`/quiz`);
  } catch (error) {
    console.error("Erreur lors du chargement des questions :", error);
  }
};


onMounted(fetchThemes);
</script>

<template>
  <div class="container">
    <h1>Choisissez un thème</h1>
    <div class="grid-container">
      <div v-for="theme in themes" :key="theme.theme" class="theme-item">
        <span class="theme-title">{{ theme.theme }}</span>
        <div class="subtheme-container">
          <button v-for="sub in theme.subthemes" :key="sub" @click="goToQuiz(sub)" class="theme-button">
            {{ sub }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>


<style scoped>
.container {
  text-align: center;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

h1 {
  margin-bottom: 20px;
}

.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(25em, 1fr)); /* Ajustez la taille minimale des colonnes */
  gap: 2em; /* Espace entre les éléments de la grille */
  width: 100%;
  max-width: 100em; /* Ajuste la largeur */
}

.theme-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}
.theme-title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
  display: block;
}

.subtheme-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
  justify-content: center; /* Centre les éléments verticalement */
  align-items: center;     /* Centre les éléments horizontalement */
  padding: 1em;
}

.theme-button {
  background-color: #5c6379;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s ease;
  width: 100%;
  max-width: 25em;
  text-align: center;
  font-size: 1rem;
  height: 3.5em;
}

.theme-button:hover {
  background-color: #0056b3;
}
</style>