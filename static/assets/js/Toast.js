

function ShowAlert(title, message, type, time, redirect){
    if (redirect){
        if (type === 'OK') {
            toastr.success(message, title, {
            positionClass: 'toast-bottom-right',
            closeButton: true,
            progressBar: true,
            newestOnTop: true,
            timeOut: time,
                onHidden: function () {
              window.location.replace(redirect);
            }
        });
        } else if (type === 'ERROR') {
            toastr.error(message, title, {
            positionClass: 'toast-bottom-right',
            closeButton: true,
            progressBar: true,
            newestOnTop: true,
            timeOut: time,
                onHidden: function () {
                  window.location.replace(redirect);
                }
            });
        } else if (type === 'INFO') {
            toastr.info(message, title, {
            positionClass: 'toast-bottom-right',
            closeButton: true,
            progressBar: true,
            newestOnTop: true,
            timeOut: time,
                onHidden: function () {
              window.location.replace(redirect);
            }
        });
        }
    }
    else {
        if (type === 'OK') {
            toastr.success(message, title, {
            positionClass: 'toast-bottom-right',
            closeButton: true,
            progressBar: true,
            newestOnTop: true,
            timeOut: time,
            })
        } else if (type === 'ERROR') {
            toastr.error(message, title, {
            positionClass: 'toast-bottom-right',
            closeButton: true,
            progressBar: true,
            newestOnTop: true,
            timeOut: time,
            })
        } else if (type === 'INFO') {
            toastr.info(message, title, {
            positionClass: 'toast-bottom-right',
            closeButton: true,
            progressBar: true,
            newestOnTop: true,
            timeOut: time,
            })
        }
    }
};