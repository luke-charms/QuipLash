'use strict';

//Setup global server variables
let url = '';
let players = new Map();
let playersToSockets = new Map();
let socketsToPlayers = new Map();

let audience = new Map();
let audienceToSockets = new Map();
let socketsToAudience = new Map();

let displaySockets = [];

let activePrompts = []
let promptsToPeople = new Map();
let playersToAnswers = new Map();
let answersToPlayers = new Map();
let answerVoteToPlayers = new Map();
let answersToVotes = new Map();
let promptsToAnswers = new Map();

let roundScores = new Map();
let totalScores = new Map();

let round = 1;
let promptsRemaining = 0;
let answersRemaining = 0;
let votesRemaining = 0;
let promptsToVoteRemaining = 0;

let currentPrompt = '';

let gameState = { state: 1, currentPrompt: '', currentPromptAnswers: [] };
let voteState = {playerAnswer1: '', answer1VoteNum: 0, answer1VotePlayers: [], playerAnswer2: '', answer2VoteNum: 0, answer2VotePlayers: []};

let timer = null;

var personCount = 1


//Setup HTTP API requests
var request = require('request');
var async = require('async');

//Setup express
const express = require('express');
const app = express();

//Setup socket.io
const server = require('http').Server(app);
const io = require('socket.io')(server);

//Setup static page handling
app.set('view engine', 'ejs');
app.use('/static', express.static('public'));

//Handle client interface on /
app.get('/', (req, res) => {
  res.render('client');
  url = req.protocol+"://"+req.headers.host;
});
//Handle display interface on /display
app.get('/display', (req, res) => {
  res.render('display');
  url = req.protocol+"://"+req.headers.host;
});

// URL of the backend API
const BACKEND_ENDPOINT = process.env.BACKEND || 'http://localhost:8181';


//Start the server
function startServer() {
    const PORT = process.env.PORT || 8080;
    server.listen(PORT, () => {
        console.log(`Server listening on port ${PORT}`);
    });
}

//Register player
async function handleRegister(socket, userAndPass) {
  console.log('Registering player...')

  const usernameAndPassword = userAndPass.toString().split(",");
  const player = usernameAndPassword[0]
  const register_json = {username: player, password: usernameAndPassword[1]};


  let response;
  try {
    response = await sendAzureAPI("/player/register", register_json, 'POST');
  } catch (err) {
    console.error('Http error', err);
    return new Promise((resolve) => {
      resolve(false);
    });
  }

  if (response['msg'] == 'OK') {
    announce('Welcome ' + player);
    totalScores.set(player,0);

    //Can only join the game before it has started
    if (gameState.state > 1) {
      announce('Game has already started, joining the audience');
      audience.set(player, { name: player, admin: false, state: gameState.state-1, score: 0, currentPromptQuestions: [], selfAnswer: false})
      audienceToSockets.set(player, socket);
      socketsToAudience.set(socket, player);
    } else {
      if (players.size <= 8) {
        if (players.size == 0) {
          players.set(player, { name: player, admin: true, state: 1, score: 0, currentPromptQuestions: [], selfAnswer: false});
        } else {
          players.set(player, { name: player, admin: false, state: 1, score: 0, currentPromptQuestions: [], selfAnswer: false});
        }
        playersToSockets.set(player, socket);
        socketsToPlayers.set(socket, player);
      } else {
        audience.set(player, { name: player, admin: false, state: 1, selfAnswer: false});
        audienceToSockets.set(player, socket);
        socketsToAudience.set(socket, player);
      }
    }
  } else {
    error(socket, response['msg'], false)
  }
  return new Promise((resolve) => {
    resolve(true);
  });
}

//Login player
async function handleLogin(socket, userAndPass) {
  console.log('Logging in player...')

  const usernameAndPassword = userAndPass.toString().split(",");
  const player = usernameAndPassword[0]
  const login_json = {username: player, password: usernameAndPassword[1]};

  let response;
  try {
    response = await sendAzureAPI("/player/login", login_json, 'GET');
  } catch (err) {
    console.error('Http error', err);
    return new Promise((resolve) => {
      resolve(false);
    });
  }

  if (response['msg'] == 'OK') {
    announce('Welcome ' + player);
    totalScores.set(player,0);

    //Can only join the game before it has started
    if (gameState.state > 1) {
      announce('Game has already started, joining the audience');
      audience.set(player, { name: player, admin: false, state: gameState.state-1, score: 0, currentPromptQuestions: [], selfAnswer: false})
      audienceToSockets.set(player, socket);
      socketsToAudience.set(socket, player);
    } else {
      if (players.size < 8) {
        if (players.size == 0) {
          players.set(player, { name: player, admin: true, state: 1, score: 0, currentPromptQuestions: [], selfAnswer: false});
        } else {
          players.set(player, { name: player, admin: false, state: 1, score: 0, currentPromptQuestions: [], selfAnswer: false});
        }
        playersToSockets.set(player, socket);
        socketsToPlayers.set(socket, player);
      } else {
        audience.set(player, { name: player, admin: false, state: 1, selfAnswer: false});
        audienceToSockets.set(player, socket);
        socketsToAudience.set(socket, player);
      }
    }
  } else {
    error(socket, response['msg'], false)
  }
  return new Promise((resolve) => {
    resolve(true);
  });
}

//Set all state to new prompt round
function restartState() {
  activePrompts = [];
  playersToAnswers.clear;
  answersToPlayers.clear;
  answerVoteToPlayers.clear;
  answersToVotes.clear;
  promptsToAnswers.clear;

  gameState = { state: 2, currentPrompt: '', currentPromptAnswers: [] };
  voteState = {playerAnswer1: '', answer1VoteNum: 0, answer1VotePlayers: [], playerAnswer2: '', answer2VoteNum: 0, answer2VotePlayers: []};
  for (let [player, socket] of playersToSockets) {
    var playerState = players.get(player);
    playerState.state = 1;
    const data = { gameState: gameState, me: player, players: Object.fromEntries(players), playersSize: players.size, audience: Object.fromEntries(audience), audienceSize: audience.size, voteState: voteState };
    socket.emit('state',data);
  }
  for (let [audienceMem, socket] of audienceToSockets) {
    var audienceState = audience.get(audienceMem);
    audienceState.state = 1;
    const data = { gameState: gameState, me: audienceMem, players: Object.fromEntries(players), playersSize: players.size, audience: Object.fromEntries(audience), audienceSize: audience.size, voteState: voteState };
    socket.emit('state',data);
  }
  for (let i = 0; i < displaySockets.length; i++) {
    const data = { gameState: gameState, me: null, players: Object.fromEntries(players), playersSize: players.size, audience: Object.fromEntries(audience), audienceSize: audience.size, voteState: voteState };
    displaySockets[i].emit('state',data);
  }
  console.log('Reset game state!');
}

//Update state of all  *players*  and  *audience*  and  *game state*
function updateAll() {
  console.log('Updating all players');
  for (let [player, socket] of playersToSockets) {
    updatePlayer(socket);
  }
  for (let [audience, socket] of audienceToSockets) {
    updateAudience(socket);
  }
  for (let i = 0; i < displaySockets.length; i++) {
    const data = { gameState: gameState, me: null, players: Object.fromEntries(players), playersSize: players.size, audience: Object.fromEntries(audience), audienceSize: audience.size, voteState: voteState };
    displaySockets[i].emit('state',data);
  }
  console.log(gameState);
  console.log(voteState);
  console.log('players size: ' + players.size);
  console.log('audience size: ' + audience.size);
}

//Update one player
function updatePlayer(socket) {
  const playerName = socketsToPlayers.get(socket);
  const player = players.get(playerName);
  const data = { gameState: gameState, me: player, players: Object.fromEntries(players), playersSize: players.size, audience: Object.fromEntries(audience), audienceSize: audience.size, voteState: voteState };
  socket.emit('state',data);
  console.log(player);
}

//Update one audience
function updateAudience(socket) {
  const audienceName = socketsToAudience.get(socket);
  const audienceState = audience.get(audienceName);
  const data = { gameState: gameState, me: audienceState, players: Object.fromEntries(players), playersSize: players.size, audience: Object.fromEntries(audience), audienceSize: audience.size, voteState: voteState };
  socket.emit('state',data);
  console.log(audience);
}

//Prompt created
async function handlePrompt(socket, prompt) {
  var playerName = socketsToPlayers.get(socket);
  var person = null;
  if (playerName == undefined) {
    var audienceName = socketsToAudience.get(socket);
    person = audience.get(audienceName);
  } else {
    person = players.get(playerName);
  }
  console.log('Prompt created: ' + prompt);
  activePrompts.push(prompt);
  promptsToPeople.set(prompt, person);

  //Update player state
  person.state = 2;

  //Call prompt create method for function API
  const prompt_json = {text: prompt, username: playerName };
  let response;
  try {
    response = await sendAzureAPI("/prompt/create", prompt_json, 'POST');
  } catch (err) {
    console.error('Http error', err);
    return new Promise((resolve) => {
      resolve(false);
    });
  }

  //Check if all prompts have been submitted
  promptsRemaining--;
  if (promptsRemaining == 0) {
    announce('All prompts answered!')
    //endPrompts();
  }
}

//Answer created
function handleAnswer(socket, answer) {
  console.log("Answer recevied: " + answer)
  var playerName = socketsToPlayers.get(socket);
  var playerState = players.get(playerName);
  answersToPlayers.set(answer, playerName);
  if (playersToAnswers.get(playerName) == undefined) {
    playersToAnswers.set(playerName, [answer]);
  } else {
    var totalAnswers = playersToAnswers.get(playerName)
    totalAnswers.push(answer);
    playersToAnswers.set(playerName, totalAnswers);
  }

  console.log(playersToAnswers.get(playerName));

  var existingAnswer = promptsToAnswers.get(playerState.currentPromptQuestions[0]);
  if (existingAnswer == undefined) {
    promptsToAnswers.set(playerState.currentPromptQuestions[0], answer);
  } else {
    var answers = [existingAnswer, answer];
    promptsToAnswers.set(playerState.currentPromptQuestions[0], answers);
  }
  if (playerState.currentPromptQuestions.length > 1) {
    playerState.currentPromptQuestions.shift();
  } else {
    playerState.state = 3;
  }

  //Check if all answers have been submitted
  answersRemaining--;
  if (answersRemaining == 0) {
    announce('All answers received!')
    //endAnswers();
  }
}

//Vote on prompt
function handleVote(socket, votedAnswerNumber) {
  //Get the answer that was voted for
  const votedAnswer = gameState.currentPromptAnswers[votedAnswerNumber-1];
  console.log("Answer voted for: " + votedAnswer)

  //Add one to number of votes for that answer
  var numVotes = answersToVotes.get(votedAnswer);

  if (numVotes == undefined) {
    answersToVotes.set(votedAnswer,1);
  } else {
    answersToVotes.set(votedAnswer,numVotes+1);
  }

  //Add to the list of people who voted for
  var answerVotedPeople = answerVoteToPlayers.get(votedAnswer);

  //Advance player (or audience) state
  var playerName = socketsToPlayers.get(socket);

  console.log(playerName);

  if (playerName == undefined) {
    playerName = socketsToAudience.get(socket);
    var audienceState = audience.get(playerName);
    audienceState.state = 4;
  } else {
    var playerState = players.get(playerName);
    playerState.state = 4;
  }
  if (answerVotedPeople == undefined) {
      answerVoteToPlayers.set(votedAnswer,[playerName]);
  } else {
      var totalPlayers = answerVoteToPlayers.get(votedAnswer);
      totalPlayers.push(playerName);
      answerVoteToPlayers.set(votedAnswer,totalPlayers);
  }


  //Check if all votes have been submitted
  votesRemaining--;
  if (votesRemaining == 0) {
    announce('All votes received!')
    //endVotes();
  }
}

//Next next button press
function handleNext() {
  if (gameState.state != 6) {
    advanceGame();
  } else {
    console.log('Going to next vote')
    //cycle through each individual answer to vote on
    promptsToVoteRemaining--;
    console.log('Num prompts to vote remaining: ' + promptsToVoteRemaining);
    if (promptsToVoteRemaining == 0) {
      var firstPrompt = Array.from(promptsToAnswers.keys())[0];
      promptsToAnswers.delete(firstPrompt)
      endScores();
    } else {
      var firstPrompt = Array.from(promptsToAnswers.keys())[0];
      promptsToAnswers.delete(firstPrompt)
      for (const [playerName, player] of players) {
        player.selfAnswer = false;
      }
      startVotes();
    }
  }
}

//Chat message
function handleChat(message) {
    console.log('Handling chat: ' + message); 
    io.emit('chat',message);
}

//Handle announcements
function announce(message) {
  console.log('Announcement: ' + message);
  io.emit('chat',message);
}

//Handle errors
function error(socket, message, halt) {
  console.log('Error: ' + message);
  socket.emit('fail', message);
  if (halt) {
    socket.disconnect();
  }
}

function handleAdmin(player, action) {
  const selectPlayer = players.get(player);
  console.log(selectPlayer);
  if (selectPlayer.admin != true) {
    console.log('Failed admin action from player ' + player + ' for ' + action);
    return;
  }
  
  if (action == 'start' && gameState.state == 1) {
    startGame();
  } else if (action = 'next') {
    goNext();
  } else {
    console.log('Unknown admin action: ' + action);
  }
}

function sendAzureAPI(azureFunction, json_body, httpMethod) {
  return new Promise((resolve) => {
    setTimeout(() => {
      var out_body = json_body;
      if (httpMethod == 'POST') {
        request.post({url: BACKEND_ENDPOINT + azureFunction + '', json: true, body: out_body}, function (error, response, body) {
          console.log('statusCode:', response && response.statusCode);
          console.log('body:', body);
          console.error('error:', error);
          resolve(body);
        }, 4000);
      } else if (httpMethod == 'GET') {
        request.get({url: BACKEND_ENDPOINT + azureFunction + '', json: true, body: out_body}, function (error, response, body) {
          console.log('statusCode:', response && response.statusCode);
          console.log('body:', body);
          console.error('error:', error);
          resolve(body);
        }, 4000);
      } else if (httpMethod == 'PUT') {
        request.put({url: BACKEND_ENDPOINT + azureFunction + '', json: true, body: out_body}, function (error, response, body) {
          console.log('statusCode:', response && response.statusCode);
          console.log('body:', body);
          console.error('error:', error);
          resolve(body);
        }, 4000);
      } else {
        console.error('Invalid HTTP Method: ' + httpMethod);
      }
  });
});}

//Advance game state
function advanceGame() {
  console.log('Going to next stage...');
  gameState.state++;

  //Check which part of game should be started
  switch (gameState.state) {
    case 3:
      endPrompts();
      startAnswers();
      break;
    case 4:
      endAnswers();
      startVotes();
      break;
    case 5:
      endVotes();
      startResults();
      break;
    case 6:
      endResults();
      startScores();
      break;
    case 7:
      endScores();
      break;
  }
}

//Start the game
function startGame() {
  console.log('Starting the game now');
  announce('Game starting...');

  //Advance the game
  gameState.state = 2;
  startPrompts();
  
}

//Start the prompts stage
function startPrompts() {
  console.log('Starting prompts section');
  announce('Please send in your prompts');

  //Update all players and audience to correct state
  for (const [playerName, player] of players) {
    player.state = 1;
  }
  for (const [audienceName, audienceMem] of audience) {
    audienceMem.state = 1;
  }

  promptsRemaining = players.size + audience.size;
  
  /*
  //Start the timer
  console.log('Starting the timer: ' + state.countdown);
  timer = setInterval(() => {
    tickGame();
  }, 1000);
  */
}

//End prompts
function endPrompts() {
  console.log('Prompt round ending...');

  // Prompts are correctly submitted to API
  console.log('Storing prompts in azure database...');
  for (const [prompt, player] of promptsToPeople) {
    const prompt_json = {text: prompt, username: player };
    //sendAzureAPI("prompt/create", prompt_json);
  }
}

//Start the answers stage
async function startAnswers() {
  console.log('Starting to submit answers');
  announce('Submit your answers to the prompts');
  
  /*
  //Start the timer
  console.log('Starting the timer: ' + state.countdown);
  timer = setInterval(() => {
    tickGame();
  }, 1000);
  */

  //Update all players and audience to correct state
  for (const [playerName, player] of players) {
    player.state = 2;
  }
  for (const [audienceName, audienceMem] of audience) {
    audienceMem.state = 2;
  }

  var numOfPrompts;
  if (players.size % 2 == 0) {
    numOfPrompts = (players.size / 2);
  } else {
    numOfPrompts = (players.size);
  }

  console.log('Number of prompts required is: ' + numOfPrompts);

  var usernames =  Array.from(players.keys());
  const find_prompts_json = {players:  usernames, language: "en"};

  const assignPrompts = [];

  //First, get the API prompts (50%) if not empty...
  var counter = 0;
  var empty = false;

  let output;
  try {
    output = await sendAzureAPI("/utils/get", find_prompts_json, "GET");
  } catch (err) {
    console.error('Http error', err);
    output = [];
  }

  if (output.length == 0) {empty = true;}
  while (counter != (Math.floor(numOfPrompts / 2)) && empty == false) {
    const randomPrompt = output[Math.floor(Math.random()*output.length)];
    const promptText = randomPrompt['text'];
    if (!assignPrompts.includes(promptText)) {
      assignPrompts.push(promptText);
      counter++;
    }
  }
  //Then, get the local-stored prompts (50%)
  while (counter != numOfPrompts) {
    const randomPrompt = activePrompts[Math.floor(Math.random()*activePrompts.length)];
    if (!assignPrompts.includes(randomPrompt)) {
      assignPrompts.push(randomPrompt);
      counter++;
    }
  }

  //Set number of answers expecting to receive
  console.log('assigned prompts: ' + assignPrompts);
  if (players.size % 2 == 0) {
    answersRemaining = players.size;
  } else {
    answersRemaining = players.size * 2;
  }

  //Assign prompts to players
  var counter = 0;
  if (players.size % 2 == 0) {
    for (let [socket, player] of socketsToPlayers) {
      var thisPlayerState = players.get(player);
      thisPlayerState.currentPromptQuestions = [assignPrompts[counter]];
      counter++;
      if (counter == assignPrompts.length) {counter = 0;}
    }
  } else {
    for (let [socket, player] of socketsToPlayers) {
      var thisPlayerState = players.get(player);
      if (counter == (numOfPrompts-1)) {
        thisPlayerState.currentPromptQuestions = [assignPrompts[counter], assignPrompts[0]];
      } else {
        thisPlayerState.currentPromptQuestions = [assignPrompts[counter], assignPrompts[counter+1]];
      }
      counter++;
    }
  }

  //Assign all prompts to players
  updateAll();
}

//End answers
function endAnswers() {
  console.log('Answer round ending...');
  promptsToVoteRemaining = promptsToAnswers.size;
  
  for (let [socket, player] of socketsToPlayers) {
    var playerState = players.get(player);
    playerState.currentPromptQuestions = [];
    if (playersToAnswers.get(player) == undefined) {
      playersToAnswers.set(player, ['[No Answer]']);
      answersToPlayers.set(['[No Answer]'], player);
      
      var existingAnswer = promptsToAnswers.get(playerState.currentPromptQuestions[0]);
      if (existingAnswer == undefined) {
        promptsToAnswers.set(playerState.currentPromptQuestions[0], answer);
      } else {
        var answers = existingAnswer.push('[No Answer]');
        promptsToAnswers.set(playerState.currentPromptQuestions[0], answers);
      }
      if (playerState.currentPromptQuestions.size > 0) {
        playerState.currentPromptQuestions = playerState.currentPromptQuestions.shift;
      } else {
        playerState.state = 3;
        playerState.currentPromptQuestions = [];
      }
    } else {

    }
  }
}

//Start the votes stage
function startVotes() {
  gameState.state = 4;
  announce('Vote for your favourite answer');

  //Update all players and audience to correct state
  for (const [playerName, player] of players) {
    player.state = 3;
  }
  for (const [audienceName, audienceMem] of audience) {
    audienceMem.state = 3;
  }

  //empty maps
  answersToVotes.clear();
  answerVoteToPlayers.clear();

  //Set number of votes expecting to receive
  votesRemaining = (players.size + audience.size) - 2;

  //Get current prompt
  currentPrompt = Array.from(promptsToAnswers.keys())[0];
  gameState.currentPrompt = currentPrompt;
  const currentAnswers = promptsToAnswers.get(currentPrompt);
  gameState.currentPromptAnswers = currentAnswers;
  console.log('current answers is: ' + currentAnswers);
  console.log(playersToAnswers);

  //If its your answer being displayed, then don't show vote
  for (let [player, answers] of playersToAnswers) {
    var playerState = players.get(player);
    if (answers.includes(currentAnswers[0]) || answers.includes(currentAnswers[1])) {
      playerState.selfAnswer = true;
      playerState.state = 4;
    } else {
      playerState.selfAnswer = false;
      playerState.state = 3;
    }
  }

  updateAll();

  /*
  //Start the timer
  console.log('Starting the timer: ' + state.countdown);
  timer = setInterval(() => {
    tickGame();
  }, 1000);
  */
}

//End votes
function endVotes() {
  console.log('Voting round ending...');

  roundScores.clear();

  const currentAnswers = promptsToAnswers.get(currentPrompt);
  var answer1Votes = answersToVotes.get(currentAnswers[0]);
  if (answer1Votes == undefined) {answer1Votes = 0;}
  var answer2Votes = answersToVotes.get(currentAnswers[1]);
  if (answer2Votes == undefined) {answer2Votes = 0;}

  const score1 = round * Number(answer1Votes) * 100;
  const score2 = round * Number(answer2Votes) * 100;

  console.log(answersToPlayers);
  const player1 = answersToPlayers.get(currentAnswers[0]);
  const player2 = answersToPlayers.get(currentAnswers[1]);

  roundScores.set(player1, score1);
  roundScores.set(player2, score2);

  var sorted_roundScores = new Map([...roundScores].sort((a, b) => b[1] - a[1]))
  console.log(sorted_roundScores);

  console.log("answer vote to players: ");
  console.log(answerVoteToPlayers);

  var answer1VotePlayersArray = answerVoteToPlayers.get(currentAnswers[0]);
  if (answer1VotePlayersArray == undefined) {answer1VotePlayersArray = [];}
  var answer2VotePlayersArray = answerVoteToPlayers.get(currentAnswers[1]);
  if (answer2VotePlayersArray == undefined) {answer2VotePlayersArray = [];}

  voteState = {playerAnswer1: player1, answer1VoteNum: Number(answer1Votes), answer1VotePlayers: answer1VotePlayersArray, playerAnswer2: player2, answer2VoteNum: Number(answer2Votes), answer2VotePlayers: answer2VotePlayersArray};

  for (let [player, socket] of playersToSockets) {
    var playerState = players.get(player);
    var playerRoundScore = roundScores.get(player);
    if (!(playerRoundScore == undefined)) {
      console.log(playerRoundScore);
      var currentScore = totalScores.get(player);
      totalScores.set(player, currentScore + playerRoundScore);
      playerState.score = currentScore + playerRoundScore;
    }
  }
  updateAll();
}

//Start the results stage
function startResults() {
  console.log('Starting results stage');
  announce('View the results of the round');


  //Update all players and audience to correct state
  //for (const [playerName, player] of players) {
  //  player.state = 4;
  //}
  //for (const [audienceName, audienceMem] of audience) {
  //  audienceMem.state = 4;
  //}
  
  /*
  //Start the timer
  console.log('Starting the timer: ' + state.countdown);
  timer = setInterval(() => {
    tickGame();
  }, 1000);
  */
}

//End results
function endResults() {
  console.log('Results round ending...');
}

//Start the scores stage
function startScores() {
  console.log('Starting scores stage');
  announce('View scores from the game');

  players = sort_object(players);
  updateAll();

  /*
  //Start the timer
  console.log('Starting the timer: ' + state.countdown);
  timer = setInterval(() => {
    tickGame();
  }, 1000);
  */
  
  //Advance the game
  gameState.state = 6;
}

//End scores
function endScores() {
  //If no more rounds to come, end game
  round++;
  console.log('round is: ' + round)
  if (round > 3) {
    console.log('Scores stage ending...');
    endGame();
  } else {
  //start new round
  restartState();
  startPrompts();
  }
}

//End game
async function endGame() {
  gameState.state = 7;
  console.log('Game over');

  //Call player update function from API to update player games/scores
  /*
  for (let [player, socket] of playersToSockets) {
    var playerState = players.get(player);
    const update_json = {username: player, add_to_games_played: 1 , add_to_score: playerState.score };
    let response;
    try {
      response = await sendAzureAPI("/player/update", update_json, 'PUT');
    } catch (err) {
      console.error('Http error', err);
      return new Promise((resolve) => {
        resolve(false);
      });
    }
  }
  */
}

function sort_object(map) {
  var sorted_map_by_values = new Map([...map].sort((a, b) => b[1].score - a[1].score))
  return(sorted_map_by_values)
}

//Handle new connection
io.on('connection', socket => { 
  console.log('New connection');

  if (socket.handshake.headers.referer.toString().includes('display')) {
    displaySockets.push(socket);
    socket.emit('urlUpdate',url);
    updateAll();
  }

  //Handle player register being received
  socket.on('register', async userAndPass => {
    if (socketsToPlayers.has(socket)) return;
    await handleRegister(socket, userAndPass);    
    updateAll();
  });

  //Handle player login being received
  socket.on('login', async userAndPass => {
    if (socketsToPlayers.has(socket)) return;
    await handleLogin(socket, userAndPass);
    updateAll();
  });

  //Handle create prompt being received
  socket.on('prompt', async prompt => {
    await handlePrompt(socket, prompt);
    updateAll();
  });

  //Handle answer prompt being received
  socket.on('answer', answer => {
    handleAnswer(socket, answer);
    updateAll();
  });

  //Handle prompt vote being received
  socket.on('vote', votedAnswerNum => {
    handleVote(socket, votedAnswerNum);
    updateAll();
  });

  //Handle next prompt being received
  socket.on('next', () => {
    handleNext();
    updateAll();
  });

  //Handle on chat message received
  socket.on('chat', message => {
    handleChat(message);
  });

  //Handle disconnection
  socket.on('disconnect', () => {
    console.log('Dropped connection');
  });

  //Handle admin press
  socket.on('admin', action => {
    if (!socketsToPlayers.has(socket)) return;    
    handleAdmin(socketsToPlayers.get(socket), action);
    updateAll();
  });

});

//Start server
if (module === require.main) {
  startServer();
}

module.exports = server;