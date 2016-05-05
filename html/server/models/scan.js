var mongoose = require('mongoose');

var scanDetailSchema = {
    hostname: {
        type: String,
        required: true
    },
    distribution: {
        codename: {
            type: String
        },
        description: {
            type: String
        },
        majversion: {
            type: String
        },
        patch_release: {
            type: String
        },
        vendor: {
            type: String
        },
        version: {
            type: String
        }
    },
    modules: Object,
    scan_time: {
        type: Date, default: Date.now
    },
    summary: {
        criticals: {
            type: Number, default: 0
        },
        infos: {
            type: Number, default: 0
        },
        max_severity: {
            type: String, required: true
        },
        warnings: {
            type: Number, default: 0
        }
    }
};

module.exports = new mongoose.Schema(scanDetailSchema);
module.exports.scanDetailSchema = scanDetailSchema;
