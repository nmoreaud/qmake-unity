#ifndef WEAPONSLOT_H
#define WEAPONSLOT_H

#include "Slot.h"

namespace qge{

class EquipableItem;

class WeaponSlot : public Slot
{
public:
    bool canBeEquipped(EquipableItem* item);
    void use();
};

}
#endif
