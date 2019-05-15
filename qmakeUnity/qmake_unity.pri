UNITY_SCRIPTS_DIR = $$clean_path($${PWD})

!defined(PROJECTS_ROOT, var) {
    PROJECTS_ROOT=$$clean_path($${PWD}/../)
}
!defined(UNITY_TMP_DIR, var) {
    UNITY_TMP_DIR=$$clean_path($$PROJECTS_ROOT/tmp/Build_Qt/unity/)
}
UNITY_TMP_DIR_SUFFIX = $$relative_path($$_PRO_FILE_PWD_, $$PROJECTS_ROOT)
UNITY_DIR = $$UNITY_TMP_DIR/$$UNITY_TMP_DIR_SUFFIX/


!defined(UNITY_MOC_MODE, var) {
    UNITY_MOC_MODE = MOC_LVL_2
}

#!build_pass { # do this action only once if config = debug + release
    !equals(UNITY_BUILD_DISABLE, "1") {
        defined(UNITY_BUILD, var) {
            !count(SOURCES, 1) {
                mkpath($$UNITY_DIR)
                UNITY_SOURCES_FILE_LOCALVAR = $${UNITY_DIR}unitySources.txt
                write_file($$UNITY_SOURCES_FILE_LOCALVAR, SOURCES)
                system(cd $$_PRO_FILE_PWD_ & python $$UNITY_SCRIPTS_DIR/qmake_unity.py update incremental "$$UNITY_DIR" "$$UNITY_SOURCES_FILE_LOCALVAR")
                UNITY_GENERATED_PRI_LINES = $$cat($${UNITY_DIR}unity.pri, lines)
                for(UNITY_GENERATED_PRI_LINE, UNITY_GENERATED_PRI_LINES) {
                    eval($$UNITY_GENERATED_PRI_LINE)
                }
            }

            equals(UNITY_MOC_MODE, MOC_LVL_2) {
                !count(HEADERS, 1) {
                    mkpath($$UNITY_DIR)
                    UNITY_HEADERS_FILE_LOCALVAR = $${UNITY_DIR}unityHeaders.txt
                    write_file($$UNITY_HEADERS_FILE_LOCALVAR, HEADERS)
                    system(cd $$_PRO_FILE_PWD_ & python $$UNITY_SCRIPTS_DIR/unity_moc_headers.py generate_groups "$$UNITY_HEADERS_FILE_LOCALVAR")
                    UNITY_GENERATED_PRI_LINES = $$cat($${UNITY_DIR}unity_headers.pri, lines)
                    for(UNITY_GENERATED_PRI_LINE, UNITY_GENERATED_PRI_LINES) {
                        eval($$UNITY_GENERATED_PRI_LINE)
                    }
                }
            }
        }
    }
    else {
        !build_pass:message("UNITY_BUILD_DISABLE is set.")
    }
#}
