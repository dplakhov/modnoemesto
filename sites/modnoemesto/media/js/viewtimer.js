CameraTimer = function (container) {
    if (container == undefined) return;
    function toStr(i) {
        return i < 10 && "0" + i || i;
    }
    var hday = $(".day", container),
        hhour = $(".hour", container),
        hminute = $(".minute", container),
        hsecond = $(".second", container);
    var day = hday && parseInt(hday.html()) || 0,
        hour = hhour && parseInt(hhour.html()) || 0,
        minute = hminute && parseInt(hminute.html()) || 0,
        second = hsecond && parseInt(hsecond.html()) || 0;


    this.intervalID = undefined;

    this.start = function () {
        if (this.intervalID != undefined) this.stop();
        this.intervalID = setInterval(function(){
            second--;
            if (second < 0) {
                if (hour == minute == hour == 0) {
                    this.stop();
                    return;
                }
                second = 59;
                minute--;
                if (minute < 0) {
                    minute = 59;
                    hour--;
                    if (hour < 0) {
                        hour = 23;
                        day--;
                        hday.html(day);
                    }
                    hhour.html(toStr(hour));
                }
                hminute.html(toStr(minute));
            }
            hsecond.html(toStr(second));
        }, 1000);
    }
    this.stop = function () {
        clearInterval(this.intervalID);
        this.intervalID = undefined;
    }
}