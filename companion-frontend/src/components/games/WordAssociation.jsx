import React from 'react';
import { speak } from '../../services/speech';

function WordAssociation(props) {
  var question = React.useState(null);
  question = question[0];
  var setQuestion = question[1];
  
  var questionNumber = React.useState(1);
  questionNumber = questionNumber[0];
  var setQuestionNumber = questionNumber[1];
  
  var score = React.useState(0);
  score = score[0];
  var setScore = score[1];
  
  var status = React.useState('loading');
  status = status[0];
  var setStatus = status[1];
  
  var selectedIndex = React.useState(null);
  selectedIndex = selectedIndex[0];
  var setSelectedIndex = selectedIndex[1];
  
  var feedbackMessage = React.useState('');
  feedbackMessage = feedbackMessage[0];
  var setFeedbackMessage = feedbackMessage[1];
  
  var onComplete = props.onComplete;
  var onClose = props.onClose;
  
  function loadQuestion() {
    setStatus('loading');
    setSelectedIndex(null);
    setFeedbackMessage('');
    
    fetch('/api/games/word-question?user_id=1')
      .then(function(response) {
        return response.json();
      })
      .then(function(data) {
        setQuestion(data);
        setStatus('question');
        if (data.question) {
          speak("Can you help me with this one John? " + data.question);
        }
      })
      .catch(function(err) {
        console.error('Error loading question:', err);
        setStatus('error');
      });
  }
  
  React.useEffect(function() {
    loadQuestion();
  }, []);
  
  function handleAnswer(index) {
    if (!question || status !== 'question') {
      return;
    }
    
    setSelectedIndex(index);
    setStatus('answered');
    
    var isCorrect = index === question.correct_index;
    
    if (isCorrect) {
      setScore(score + 1);
      setFeedbackMessage(question.encouragement || "Well done John!");
      speak(question.encouragement || "Well done John!");
    } else {
      var correctAnswer = question.choices[question.correct_index];
      setFeedbackMessage("Never mind John, the answer was " + correctAnswer);
      speak("Never mind John, the answer was " + correctAnswer);
    }
    
    fetch('/api/games/answer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: 1,
        correct: isCorrect,
        question_topic: question.word || ''
      })
    })
    .catch(function(err) {
      console.error('Error submitting answer:', err);
    });
    
    setTimeout(function() {
      if (questionNumber < 3) {
        setQuestionNumber(questionNumber + 1);
        loadQuestion();
      } else {
        setStatus('complete');
        speak("Well done John, you got " + score + " out of 3!");
      }
    }, 3000);
  }
  
  function handlePlayAgain() {
    setQuestionNumber(1);
    setScore(0);
    loadQuestion();
  }
  
  function handleFinished() {
    if (onComplete) {
      onComplete();
    }
  }
  
  var containerStyle = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#f5f5f5',
    zIndex: 160,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    padding: '20px'
  };
  
  var loadingStyle = {
    fontSize: '24px',
    color: '#666',
    textAlign: 'center',
    marginTop: '100px'
  };
  
  var promptStyle = {
    fontSize: '24px',
    color: '#666',
    textAlign: 'center',
    marginBottom: '20px',
    marginTop: '30px'
  };
  
  var questionTextStyle = {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#185FA5',
    textAlign: 'center',
    marginBottom: '40px',
    padding: '0 20px'
  };
  
  var counterStyle = {
    fontSize: '18px',
    color: '#999',
    marginBottom: '20px'
  };
  
  var buttonContainerStyle = {
    display: 'flex',
    flexDirection: 'column',
    width: '100%',
    maxWidth: '400px'
  };
  
  function getButtonStyle(index) {
    var baseStyle = {
      width: '100%',
      height: '80px',
      fontSize: '24px',
      backgroundColor: '#F1EFE8',
      border: '2px solid #cccccc',
      borderRadius: '12px',
      marginBottom: '15px',
      cursor: 'pointer'
    };
    
    if (selectedIndex !== null && status === 'answered') {
      if (index === question.correct_index) {
        baseStyle.backgroundColor = '#3B6D11';
        baseStyle.color = 'white';
      } else if (index === selectedIndex) {
        baseStyle.backgroundColor = '#A32D2D';
        baseStyle.color = 'white';
      }
    }
    
    return baseStyle;
  }
  
  var feedbackStyle = {
    fontSize: '24px',
    fontWeight: 'bold',
    color: '#3B6D11',
    textAlign: 'center',
    marginTop: '30px',
    padding: '20px',
    backgroundColor: '#e8f5e9',
    borderRadius: '10px'
  };
  
  var completeContainerStyle = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100%'
  };
  
  var completeTitleStyle = {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#3B6D11',
    textAlign: 'center',
    marginBottom: '50px'
  };
  
  var buttonStyle = {
    width: '200px',
    height: '70px',
    fontSize: '22px',
    color: 'white',
    backgroundColor: '#185FA5',
    border: 'none',
    borderRadius: '12px',
    marginBottom: '20px',
    cursor: 'pointer'
  };
  
  var finishButtonStyle = {
    width: '200px',
    height: '70px',
    fontSize: '22px',
    color: 'white',
    backgroundColor: '#3B6D11',
    border: 'none',
    borderRadius: '12px',
    cursor: 'pointer'
  };
  
  if (status === 'loading') {
    return React.createElement('div', { style: containerStyle },
      React.createElement('div', { style: loadingStyle }, "Getting your question ready John...")
    );
  }
  
  if (status === 'error') {
    return React.createElement('div', { style: containerStyle },
      React.createElement('div', { style: loadingStyle }, "Could not load question"),
      React.createElement('button', { style: buttonStyle, onClick: loadQuestion }, "Try Again"),
      React.createElement('button', { style: finishButtonStyle, onClick: onClose }, "Close")
    );
  }
  
  if (status === 'complete') {
    return React.createElement('div', { style: containerStyle },
      React.createElement('div', { style: completeContainerStyle },
        React.createElement('div', { style: completeTitleStyle }, 
          "Well done John! You got " + score + " out of 3!"
        ),
        React.createElement('button', { style: buttonStyle, onClick: handlePlayAgain }, "Play again"),
        React.createElement('button', { style: finishButtonStyle, onClick: handleFinished }, "Finished")
      )
    );
  }
  
  return React.createElement('div', { style: containerStyle },
    React.createElement('div', { style: counterStyle }, "Question " + questionNumber + " of 3"),
    React.createElement('div', { style: promptStyle }, "Can you help me with this one John?"),
    question ? React.createElement('div', { style: questionTextStyle }, question.question) : null,
    question && question.choices ? React.createElement('div', { style: buttonContainerStyle },
      question.choices.map(function(choice, index) {
        return React.createElement('button', {
          key: index,
          style: getButtonStyle(index),
          onClick: function() { handleAnswer(index); },
          disabled: status === 'answered'
        }, choice);
      })
    ) : null,
    feedbackMessage ? React.createElement('div', { style: feedbackStyle }, feedbackMessage) : null
  );
}

export default WordAssociation;