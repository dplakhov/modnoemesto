for THEME in `ls -1` ; do
    if [ -d $THEME ] ; then
        cd $THEME
        zip -r ../$THEME.zip *
        cd -
    fi
done
