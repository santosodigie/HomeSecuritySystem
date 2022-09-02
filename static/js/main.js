var aliveSecond = 0;
var heartbeatRate = 5000;

var myChannel = "Azurcam-channel"

function keepAlive()
{
    var request = new XMLHttpRequest();
    request.onreadystatechange = function(){
        if(this.readyState === 4){
            if(this.status === 200){

                if(this.responseText !== null){
                    var date = new Date();
                    aliveSecond = data.getTime();
                    var keepAliveData = this.responseText;
                    //Converts string to a json

                }
            }
        }
    };
    request.open("GET", "keep_alive", true);
    request.send(null);
    setTimeout("keepAlive()", heartbeatRate);
}

function time()
{
    var d = new Date();
    var currentSec = d.getTime();
    if(currentSec - aliveSecond > heartbeatRate + 1000)
    {
        document.getElementById("Connection_id").innerHTML = "DEAD";
    }
    else
    {
        document.getElementById("Connection_id").innerHTML = "ALIVE";
    }
    setTimeout('time()', 1000);
}


pubnub = new Pubnub({
            publishKey : "pub-c-7317ff41-d6d6-4c5d-958e-0006f43407ae",
            subscribeKey : "sub-c-fab291ca-3e0b-42e9-bed7-23401929e441",
            uuid: "3bdca6e4-2953-11ed-a261-0242ac120002"
            });

pubnub.addListener({
        status: function(statusEvent) {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Successfully connected to Pubnub");
                publishSampleMessage();
            }

        },
        message: function(msg) {
            console.log(msg.message.title);
            console.log(msg.message.description);
        },
        presence: function(presenceEvent) {
        // This section is not important for now
        }
    })


pubnub.subscribe({
        channels: [myChannel]
        });


function publishUpdate(data, channel)
{
    pubnub.publish({
        channel: channel,
        message: data
        },
        function(status, response){
            if(status.error){
                console.log(status);
            }
            else
            {
                console.log("Message published with timetoken", response.timetoken)
            }
           }
        );
}

function handleClick(cb)
{
    if(cb.checked)
    {
        value = "ON";
    }
    else
    {
        value "OFF";
    }
    var ckbStatus = new Object();
    ckbStatus[cb.id] = value;
    var event = new Object();
    event.event = ckbStatus;
    publishUpdate(event, myChannel);
}

function logout()
{
    console.log("Logging out and unsubscribing");
    pubnub.unsubscribed({
        channels: [myChannel]
        })
    location.replace('/logout')
}