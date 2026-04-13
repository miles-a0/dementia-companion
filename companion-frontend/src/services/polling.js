// Polls backend every 60s for messages from n8n workflows
var API_BASE = 'http://173.249.40.161:8001/api';
var intervalId = null;

export function startPolling(onMessage, userId) {
  if (intervalId !== null) {
    return intervalId;
  }
  
  intervalId = setInterval(function() {
    pollNow(onMessage, userId);
  }, 60000);
  
  return intervalId;
}

export function stopPolling() {
  if (intervalId !== null) {
    clearInterval(intervalId);
    intervalId = null;
  }
}

export function pollNow(onMessage, userId) {
  var url = API_BASE + '/messages/pending?user_id=' + userId;
  
  fetch(url)
    .then(function(response) {
      return response.json();
    })
    .then(function(data) {
      if (data.message !== null && data.message !== undefined) {
        var message = data.message;
        
        if (onMessage) {
          onMessage(message);
        }
        
        var deleteUrl = API_BASE + '/messages/' + message.id;
        fetch(deleteUrl, { method: 'DELETE' })
          .then(function() {
            console.log('Marked message as spoken:', message.id);
          })
          .catch(function(err) {
            console.error('Error marking message as spoken:', err);
          });
      }
    })
    .catch(function(err) {
      console.error('Polling error:', err);
    });
}