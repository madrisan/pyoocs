var gulp        = require('gulp'),
    minifycss   = require('gulp-minify-css'),
    jshint      = require('gulp-jshint'),
    stylish     = require('jshint-stylish'),
    uglify      = require('gulp-uglify'),
    usemin      = require('gulp-usemin'),
    imagemin    = require('gulp-imagemin'),
    rename      = require('gulp-rename'),
    concat      = require('gulp-concat'),
    notify      = require('gulp-notify'),
    cache       = require('gulp-cache'),
    changed     = require('gulp-changed'),
    rev         = require('gulp-rev'),
    browserSync = require('browser-sync'),
    ngannotate  = require('gulp-ng-annotate'),
    del         = require('del'),
    less        = require('gulp-less');

gulp.task('jshint', function() {
    return gulp.src('app/scripts/**/*.js')
            .pipe(jshint())
            .pipe(jshint.reporter(stylish));
});

// Clean
gulp.task('clean', function() {
    return del(['json-server/public']);
});

// Default task
gulp.task('default', ['clean'], function() {
    gulp.start('buildless', 'usemin', 'copyviews', 'imagemin', 'copyfonts');
});

gulp.task('usemin', ['buildless', 'jshint'], function () {
    return gulp.src('./app/index.html')
            .pipe(usemin({
                css:[minifycss(), rev()],
                js: [ngannotate(), uglify(), rev()]
            }))
            .pipe(gulp.dest('json-server/public/'));
});

// Views
gulp.task('copyviews', function() {
    return gulp.src('app/views/**/*.html')
            .pipe(gulp.dest('json-server/public/views/'));
});

// Images
gulp.task('imagemin', function() {
    return del(['json-server/public/images']), gulp.src('app/images/**/*')
            .pipe(cache(imagemin({
                optimizationLevel: 3,
                progressive: true,
                interlaced: true
            })))
            .pipe(gulp.dest('json-server/public/images'))
            .pipe(notify({ message: 'Images task complete' }));
});

// Fonts
gulp.task('copyfonts', function() {
    gulp.src('./bower_components/font-awesome/fonts/**/*.{ttf,woff,eof,svg}*')
     .pipe(gulp.dest('json-server/public/fonts'));

    gulp.src('./bower_components/bootstrap/dist/fonts/**/*.{ttf,woff,eof,svg}*')
     .pipe(gulp.dest('json-server/public/fonts'));
});

// CSS
gulp.task('buildless', function() {
    return gulp.src('app/styles/**/*.less')
     .pipe(less())
     .pipe(gulp.dest('./app/styles'));
});

// Watch
gulp.task('watch', ['browser-sync'], function() {
  // Watch .js .css and .html files
  gulp.watch('{app/scripts/**/*.js,app/styles/**/*.less,app/**/*.html}', ['usemin']);

  // Watch views html files
  gulp.watch('app/views/**/*.html', ['copyviews']);

  // Watch image files
  gulp.watch('app/images/**/*', ['imagemin']);

});

gulp.task('browser-sync', ['default'], function () {
    var files = [
        'app/index.html',
        'app/views/**/*.html',
        'app/styles/**/*.css',
        'app/images/**/*.png',
        'app/scripts/**/*.js',
        'json-server/public/**/*'
    ];

    browserSync.init(files, {
        server: {
            baseDir: "json-server/public",
            index: "index.html"
        }
    });

    // Watch any files in dist/, reload on change
    gulp.watch(['json-server/public/**']).on('change', browserSync.reload);
});
