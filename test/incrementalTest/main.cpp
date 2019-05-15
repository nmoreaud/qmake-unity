#include <QCoreApplication>
#include <QTimer>

#include "taskexecutor.h"

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    TaskExecutor executor;
    QTimer::singleShot(0, &executor, SLOT(Exec()));

    return a.exec();
}
