#ifndef FACTORY_H
#define FACTORY_H

#define REGISTER_CLASS(CLASS_NAME) \
    static FactoryItem<CLASS_NAME> global_##CLASS_NAME##FactoryItem("" #CLASS_NAME);

#include <QMap>

class Task;

class Factory
{
public:
    static Factory& Instance();
    void AddTask(QString iName, Task *iTask);
    QMap<QString, Task*> GetTasks() const;

private:
    Factory();

    static Factory *_instance;
    QMap<QString, Task*> _tasks;
};

template <class F>
class FactoryItem {
public:
    FactoryItem(QString iClassName) {
        Factory::Instance().AddTask(iClassName, new F());
    }
};

#endif // FACTORY_H
