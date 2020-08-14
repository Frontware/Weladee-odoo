/**
 * insert "from. into proto's python files"
 */
const fs = require('fs');
var logs = {};
const proto_folder='Modules/Weladee_Attendances/models/grpcproto';
const done_replace = '# INSERTED CODE -- DO NOT EDIT';
const to_replace = [
    'import weladee_pb2 as weladee__pb2',
    'import odoo_pb2 as odoo__pb2',
    'import timesheet_pb2 as timesheet__pb2',
    'import expense_pb2 as expense__pb2'
]

fs.readdir(proto_folder, (err, files) => {
    files.forEach(file => {
      insertFrom(file)      
    });
});


function insertFrom(file) {  
    const f = proto_folder + '/' + file;
    //console.log('will check file ' + f)
    logs[file] = []
    logs[file].push('\n-----\nchecking file ' + f)

    fs.readFile(f, 'utf8', (e, d)=>{ 
        if (e) { 
            //console.log('error read file ' + f + ': ' + e);
            logs[file].push('error read file ' + f + ': ' + e)
            return; 
        }
        //console.log('\nread ' + f + ' = ' + d.length);
        logs[file].push('\nread ' + f + ' = ' + d.length)

        if (d.indexOf(done_replace) >= 0) {
            //console.log('there is already replacement in ' + f + '.... skip');
            logs[file].push('there is already replacement in ' + f + '.... skip');
            return;
        }

        var r = d;
        var i = 0;
        if (d.indexOf(to_replace[0]) >= 0) {
        
            r = r.replace(to_replace[0], 
                    done_replace + 
                    '\n# timestamp : ' + new Date() +
                    '\nfrom . ' + to_replace[0]);
            i++;
        } else {
            //console.log('can not found ' + to_replace[0] +' in ' + f + '.... skip.');
            logs[file].push('can not found ' + to_replace[0] +' in ' + f + '.... skip.');
            return;
        }

        if (r.indexOf(to_replace[1]) >= 0) {
        
            r = r.replace(to_replace[1], 
                    'from . ' + to_replace[1]);
            i++;
        }
        if (r.indexOf(to_replace[2]) >= 0) {
        
            r = r.replace(to_replace[2], 
                    'from . ' + to_replace[2]);
            i++;
        }
        if (r.indexOf(to_replace[3]) >= 0) {
        
            r = r.replace(to_replace[3], 
                    'from . ' + to_replace[3]);
            i++;
        }

        fs.writeFile(f, r, 'utf8', (e) => {
            if (e) { 
                //console.log('error update file ' + f + ': ' + e);
                logs[file].push('error update file ' + f + ': ' + e);
                return; 
            }
            //console.log('\nreplaced in ' + f + ': ' + i);
            logs[file].push('replaced in ' + f + ': ' + i);

            logs[file].forEach( ll => {
                console.log(ll)
            });
        });
    });
}