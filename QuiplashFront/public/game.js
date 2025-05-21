var socket = null;

//Prepare game
var app = new Vue({
    el: '#game',
    data: {
        url: '',
        errorMsg: null,
        me: { name: '', admin: false, state: 0, score: 0, currentPromptQuestions: [], selfAnswer: false },
        gameState: { state: false, currentPrompt: '', currentPromptAnswers: [] },
        voteState: {playerAnswer1: '', answer1VoteNum: 0, answer1VotePlayers: [], playerAnswer2: '', answer2VoteNum: 0, answer2VotePlayers: []},
        players: {},
        playersSize: 0,
        audience: {},
        audienceSize: 0,
        
        messages: [],
        chatmessage: '',
        usernameText: '',
        passwordText: '',
        promptInput: '',
        answerInput: '',

        selectedAnswer: -1,

        currentPromptAnswer: ''
    },
    mounted: function() {
        connect(); 
    },
    methods: {
        admin(command) {
            socket.emit('admin',command)
        },
        handleChat(message) {
            if(this.messages.length + 1 > 10) {
                this.messages.pop();
            }
            this.messages.unshift(message);
        },
        chat() {
            socket.emit('chat', this.chatmessage);
            this.chatmessage = '';
        },
        register() {
            socket.emit('register', (this.usernameText + "," + this.passwordText));
            this.usernameText = '';
            this.passwordText = '';
        },
        login() {
            socket.emit('login', (this.usernameText + "," + this.passwordText));
            this.usernameText = '';
            this.passwordText = '';
        },
        prompt() {
            socket.emit('prompt', this.promptInput),
            this.promptInput = '';
        },
        answer() {
            socket.emit('answer', this.answerInput);
            if (this.me.currentPromptQuestions.length > 1) {this.answerInput = '';}
        },
        vote1() {
            socket.emit('vote', 1);
            this.selectedAnswer = 0;
            this.answerInput = ''
        },
        vote2() {
            socket.emit('vote', 2);
            this.selectedAnswer = 1;
            this.answerInput = ''
        },
        next() {
            socket.emit('next');
            this.sort();
        },
        update(data) {
            this.me = data.me;
            this.gameState = data.gameState;
            this.players = data.players;
            this.playersSize = data.playersSize;
            this.audience = data.audience;
            this.audienceSize = data.audienceSize;
            this.voteState = data.voteState;
        },
        urlUpdate(data) {
            this.url = data;
        },
        fail(message) {
            this.errorMsg = message;
        }
    }
});

function connect() {
    //Prepare web socket
    socket = io();

    //Connect
    socket.on('connect', function() {
        //Set connected state to true
        app.gameState.state = 1;
    });

    //Handle connection error
    socket.on('connect_error', function(message) {
        alert('Unable to connect: ' + message);
    });

    //Handle disconnection
    socket.on('disconnect', function() {
        alert('Disconnected');
    });

    //Handle incoming chat message
    socket.on('chat', function(message) {
        app.handleChat(message);
    });

    //Handle error messages
    socket.on('fail', function(message) {
        app.fail(message);
    });

    socket.on('state', function(data) {
        app.update(data);
    });

    socket.on('receivePrompt', function(data) {
        app.currentPromptQuestion = data;
    });

    socket.on('urlUpdate', function(data) {
        app.urlUpdate(data);
    });

}
