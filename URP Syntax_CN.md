# URP Syntax

以下是基于 UR 机器人程序（URP）格式规范，结合 XML 结构提炼的完整语法说明，包含节点层级、属性定义和示例

## 1. 根节点：<URProgram>

#### 作用

表示整个 UR 程序的根容器，包含程序元数据和核心内容。

#### 属性（必填）

| 属性名                              | 类型   | 说明                                                        | 示例值                                               |
| ----------------------------------- | :----- | ----------------------------------------------------------- | ---------------------------------------------------- |
| `name`                              | 字符串 | 程序名称                                                    | `"MyProgram"`                                        |
| `installation`                      | 字符串 | 安装配置名称（默认值：`"default"`）                         | `"custom_install"`                                   |
| `installationRelativePath`          | 字符串 | 安装路径的相对路径（默认值：`"default"`）                   | `"/installations"`                                   |
| `directory`                         | 字符串 | 程序存储目录（URSim 路径）                                  | `"/home/ur/ursim/programs"`                          |
| `createdIn`                         | 字符串 | 创建程序的 URSim 版本（格式：`"X.Y.Z"`）                    | `"5.15.0"`                                           |
| `lastSavedIn`                       | 字符串 | 最后保存程序的 URSim 版本                                   | `"5.15.0"`                                           |
| `robotSerialNumber`                 | 字符串 | 机器人序列号（如 `UR3e`、`UR10e` 的序列号）                 | `"20195599999"`                                      |
| `createdInPolyscopeProgramVersion`  | 字符串 | 创建程序的 PolyScope 版本                                   | `"2"`                                                |
| `lastSavedInPolycopeProgramVersion` | 字符串 | 最后保存程序的 PolyScope 版本                               | `"2"`                                                |
| `crcValue`                          | 字符串 | 程序校验和（需与示教器右上角的CRC值相等，这里为十进制数值） | 如果机器人上显示DF5C7C1A, 这里对于值为`"3747380250"` |

#### **子节点（必填）**

- `<kinematics>`：运动学参数配置（见下文）。
- `<children>`：程序节点容器，包含初始化、特殊序列、主程序等。



## 2. 运动学配置节点：<kinematics>

#### **作用**

定义机器人运动学参数（DH 参数）和状态。

#### **属性（必填）**

| 属性名        | 类型   | 说明                                         | 示例值            |
| ------------- | ------ | -------------------------------------------- | ----------------- |
| status        | 字符串 | 运动学状态（值："NOT_INITIALIZED", "VALID"） | "NOT_INITIALIZED" |
| validChecksum | 字符串 | 校验和有效性（"true"/"false"）               | "false"           |

#### **子节点（必填）**

以下节点均为 `<kinematics>` 的子节点，都需包含 `value` 属性（6 个参数逗号分隔）：

| 节点名            | 说明                  | `value` 格式                                 |
| ----------------- | --------------------- | -------------------------------------------- |
| `<deltaTheta>`    | 关节角度增量          | `"0.0, 0.0, 0.0, 0.0, 0.0, 0.0"`             |
| `<a>`             | 连杆长度（DH 参数）   | `"-0.425, -0.3922, 0.0, 0.0, 0.0, 0.0"`      |
| `<d>`             | 连杆偏移（DH 参数）   | `"0.1625, 0.0, 0.0, 0.1333, 0.0997, 0.0996"` |
| `<alpha>`         | 连杆扭转角（DH 参数） | `"1.5708, 0.0, 0.0, 1.5708, -1.5708, 0.0"`   |
| `<jointChecksum>` | 关节校验和            | `"-1, -1, -1, -1, -1, -1"`                   |



## **3. 程序节点容器：`<children>`**

#### **作用**

包裹程序的执行节点，如初始化、特殊序列、主程序等。

#### **子节点类型**

##### 3.1 **初始化节点：`<InitVariablesNode>`**

- **作用**：标记程序初始化（无属性和子节点）。

```html
<InitVariablesNode>
```

##### 3.2 **特殊序列节点：`<SpecialSequence>`**

- **作用**：定义”开始前“（`BeforeStart`）操作。
- 属性：
  - `type`（必填）：`"BeforeStart"` 。
- **子节点**：如有子节点需包含 `<children>` 标签，如包裹等待指令等。

```html
<SpecialSequence type="BeforeStart">
  <children>
    <Wait type="Sleep">
      <waitTime>0.5</waitTime>
    </Wait>
  </children>
</SpecialSequence>
```



##### 3.3 **主程序节点：`<MainProgram>`**

- **作用**：主程序逻辑容器。
- **属性**：
  - `runOnlyOnce`（必填）：`"true"`（仅运行一次）或 `"false"`（循环运行）。
  - `InitVariablesNode`（必填）：`"true"`（关联初始化节点）或 `"false"`。
- **子节点**：需包含 `<children>` 标签，包裹运动指令、等待指令等。

```html
<MainProgram runOnlyOnce="true" InitVariablesNode="true">
  <children>
    <Move>...</Move>
    <Wait>...</Wait>
  </children>
</MainProgram>
```



## 4. **运动指令节点：`<Move>`**

#### **作用**

定义机器人运动（关节运动、直线运动等）。

#### **属性（必填）**

| 属性名         | 类型   | 说明                                                         | 示例值            |
| -------------- | ------ | ------------------------------------------------------------ | ----------------- |
| `motionType`   | 字符串 | 运动类型（值：`"MoveJ"`（关节运动）、`"MoveL"`（直线运动）、`"MoveC"`（圆弧运动）） | `"MoveJ"`         |
| `speed`        | 字符串 | 运动速度（关节速度：rad/s；笛卡尔速度：m/s）                 | `"1.0472"`        |
| `acceleration` | 字符串 | 加速度（关节加速度：rad/s²；笛卡尔加速度：m/s²）             | `"1.3963"`        |
| `useActiveTCP` | 字符串 | 是否使用当前 TCP（`"true"`/`"false"`）                       | `"true"`          |
| `positionType` | 字符串 | 位置类型（`"CartesianPose"`（笛卡尔坐标）、`"JointAngles"`（关节角度）） | `"CartesianPose"` |

#### **子节点（选填）**

##### 4.1 **几何特征引用：`<feature>`**

- **作用**：引用工具、工件坐标系等几何特征。
- **属性**：
  - `class`（固定值）：`"GeomFeatureReference"`。
  - `referencedName`（选填）：特征名称（如 ''Joint_0_name''、`"Tool_0"`、`"Workpiece_1"`）。

```html
<feature class="GeomFeatureReference" referencedName="Joint_0_name"/>
```



##### 4.2 **路径点容器：`<children>`**

- **作用**：包裹运动路径点（`<Waypoint>`）。

```html
<children>
  <Waypoint type="Fixed" name="Waypoint_1">...</Waypoint>
  <Waypoint type="Fixed" name="Waypoint_2">...</Waypoint>
</children>
```



## 5. **路径点节点：`<Waypoint>`**

#### **作用**

定义运动的目标位置和参数。

#### **属性（必填）**

| 属性名            | 类型   | 说明                                                         | 示例值         |
| ----------------- | ------ | ------------------------------------------------------------ | -------------- |
| `type`            | 字符串 | 路径点类型（值：`"Fixed"`（固定点）,"Relative"(相对点)，”Variable“（可变位置）） | `"Fixed"`      |
| `name`            | 字符串 | 路径点名称                                                   | `"Waypoint_1"` |
| `kinematicsFlags` | 字符串 | 运动学标志位（二进制掩码，如 `"4"`）                         | `"4"`          |

#### **子节点**

##### 5.1 **运动参数：`<motionParameters>`**

- **作用**：可选参数（如关节速度、笛卡尔速度、过渡半径等）。

```html
<motionParameters 
  jointSpeed="1.0297" 
  jointAcceleration="1.3788101090755203" 
  cartesianSpeed="0.25" 
  cartesianAcceleration="1.2" 
  blendRadius="0.012"
/>
```

##### 5.2 **位置数据：`<position>`**

- **作用**：定义位置坐标和运动学参数。
- **子节点**：
  - `<JointAngles>`：关节角度（`angles` 属性为 6 个浮点数逗号分隔）。
  - `<TCPOffset>`：TCP 偏移（`pose` 属性为 `x,y,z,rx,ry,rz`）。
  - `<Kinematics>`：运动学参数（同根节点 `<kinematics>` 结构）。

```html
<position>
  <JointAngles angles="-1.6007, -1.7271, -2.2030, -0.8080, 1.5951, -0.0310"/>
  <TCPOffset pose="0.0, 0.0, 0.12, 0.0, 0.0, 0.0"/>
  <Kinematics status="NOT_INITIALIZED" validChecksum="false">
    <deltaTheta value="0.0, 0.0, 0.0, 0.0, 0.0, 0.0"/>
    <a value="0.0, -0.425, -0.3922, 0.0, 0.0, 0.0"/>
    <d value="0.1625, 0.0, 0.0, 0.1333, 0.0997, 0.0996"/>
    <alpha value="1.570796327, 0.0, 0.0, 1.570796327, -1.570796327, 0.0"/>
    <jointChecksum value="-1, -1, -1, -1, -1, -1"/>
  </Kinematics>
</position>
```

##### 5.3 **基坐标系偏移：`<BaseToFeature>`**

- **作用**：基坐标系到目标特征的偏移（可选）。

```html
<BaseToFeature pose="0.0, 0.0, 0.0, 0.0, 0.0, 0.0"/>
```



## 6. **等待指令节点：`<Wait>`**

#### **作用**

定义程序暂停或条件等待。

#### **属性（必填）**

| 属性名 | 类型   | 说明                                                         | 示例值    |
| ------ | ------ | ------------------------------------------------------------ | --------- |
| `type` | 字符串 | 等待类型（值：`"Sleep"`、`"DigitalInput"`、`"AnalogInput"`、`"Condition"`） | `"Sleep"` |

#### **子节点（根据 `type` 不同）**

##### 6.1 **休眠等待：`type="Sleep"`**

```html
<Wait type="Sleep">
  <waitTime>0.22</waitTime> <!-- 休眠时间（秒） -->
</Wait>
```



##### 6.2 **数字输入等待：`type="DigitalInput"`**

```html
<Wait type="DigitalInput">
  <pin referencedName="digital_in[2]"/> <!-- 输入引脚 -->
  <digitalValue>1</digitalValue> <!-- 期望值（0 或 1） -->
</Wait>
```



##### 6.3 **模拟输入等待：`type="AnalogInput"`**

```html
<Wait type="AnalogInput">
  <pin referencedName="analog_in[1]"/> <!-- 输入引脚 -->
  <analogComparison>1</analogComparison> <!-- 比较方式：0=小于，1=大于，2=等于 -->
  <analogValue>4.0</analogValue> <!-- 目标值 -->
</Wait>
```



##### 6.4 **条件等待：`type="Condition"`**

```html
<Wait type="Condition">
  <expression>
    <ExpressionChar character="b"/> <!-- 拼接条件表达式字符串，如 "bflag == True" -->
    <ExpressionChar character="f"/>
    <ExpressionChar character="l"/>
    <ExpressionChar character="a"/>
    <ExpressionChar character="g"/>
    <ExpressionChar character="="/>
    <ExpressionChar character="="/>
    <ExpressionChar character="T"/>
    <ExpressionChar character="r"/>
    <ExpressionChar character="u"/>
    <ExpressionChar character="e"/>
      <!-- 更多字符节点 -->
  </expression>
</Wait>
```



## 7. 语法总结

### 7.1 **层级结构**：

- 所有子节点需通过 `<children>` 标签包裹（除叶节点外）。
- 示例：`<Move>` 的路径点需放在 `<children>` 中，`<Waypoint>` 的位置数据需放在 `<position>` 的 `<children>` 中。

### 7.2 **属性值格式**：

- 布尔值用小写（`"true"`/`"false"`）。
- 数值型属性直接用字符串表示（如 `"0.22"`、`"-1"`）。
- 数组型值用逗号分隔（如 `"1.0, 2.0, 3.0"`）。

### 7.3 **命名规范**：

- 标签名和属性名严格区分大小写（如 `<Kinematics>` 而非 `<kinematics>`）。
- 引脚命名遵循 `digital_in[N]`、`analog_in[N]` 格式（`N` 为引脚编号）。

### 7.4 **必选节点**：

- `<URProgram>` 必须包含 `<kinematics>` 和 `<children>`。
- `<Move>` 必须包含 `<feature>` 和 `<children>`。
- `<Waypoint>` 必须包含 `<position>`。



## 8. 完整URP示例

```html
<URProgram 
  name="urpTest" 
  installation="default" 
  directory="/home/ur/ursim/ursim-5.15.0.126572/programs" 
  createdIn="5.15.0" 
  lastSavedIn="5.15.0"
  robotSerialNumber="2019559999"
  createdInPolyscopeProgramVersion="2" 
  lastSavedInPolycopeProgramVersion="2" 
  crcValue="3747380250"
>
  <kinematics status="NOT_INITIALIZED" validChecksum="false">
    <deltaTheta value="0.0, 0.0, 0.0, 0.0, 0.0, 0.0"/>
    <a value="0.0, -0.425, -0.3922, 0.0, 0.0, 0.0"/>
    <d value="0.1625, 0.0, 0.0, 0.1333, 0.0997, 0.0996"/>
    <alpha value="1.570796327, 0.0, 0.0, 1.570796327, -1.570796327, 0.0"/>
    <jointChecksum value="-1, -1, -1, -1, -1, -1"/>
  </kinematics>

  <children>
    <InitVariablesNode/>
    <SpecialSequence type="BeforeStart">
      <children>
        <Wait type="Sleep">
          <waitTime>0.22</waitTime>
        </Wait>
      </children>
    </SpecialSequence>

    <MainProgram runOnlyOnce="true" InitVariablesNode="false">
      <children>
        <Move motionType="MoveJ" speed="1.0472" acceleration="1.3962634015954636" useActiveTCP="true" positionType="CartesianPose">
          <feature class="GeomFeatureReference" referencedName="Joint_0_name"/>
          <children>
            <Waypoint type="Fixed" name="Waypoint_1" kinematicsFlags="4">
              <motionParameters/>
              <position>
                <JointAngles angles="-1.6, -1.7, -2.2, -0.8, 1.6, -0.03"/>
                <TCPOffset pose="0.0, 0.0, 0.12, 0.0, 0.0, 0.0"/>
                <Kinematics status="NOT_INITIALIZED" validChecksum="false">
                  <deltaTheta value="0.0, 0.0, 0.0, 0.0, 0.0, 0.0"/>
                  <a value="0.0, -0.425, -0.3922, 0.0, 0.0, 0.0"/>
                  <d value="0.1625, 0.0, 0.0, 0.1333, 0.0997, 0.0996"/>
                  <alpha value="1.570796327, 0.0, 0.0, 1.570796327, -1.570796327, 0.0"/>
                  <jointChecksum value="-1, -1, -1, -1, -1, -1"/>
                </Kinematics>
              </position>
              <BaseToFeature pose="0.0, 0.0, 0.0, 0.0, 0.0, 0.0"/>
            </Waypoint>
          </children>
        </Move>
        <Wait type="DigitalInput">
          <pin referencedName="digital_in[0]"/>
          <digitalValue>1</digitalValue>
        </Wait>
      </children>
    </MainProgram>
  </children>
</URProgram>
```



这是根据库中urpRecipt.json生成的output_1.urp结果，本文介绍的方法带来的一个好处是可以用中文/日本/韩文等特殊字体命名你的路点节点，而这在Polyscope 本地是无法实现的.

![Screenshot 2025-04-30 181154](./pictures/Screenshot_2025-04-30_181154.png)
