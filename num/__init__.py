from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.adapters.onebot.v11 import MessageEvent, Message, MessageSegment
import random, time
# 用来缓存随机数和种子信息
random_cache = {}

num = on_command("猜数字", aliases={"num", "gnum"})


@num.handle()
async def num_handle(event: MessageEvent, args: Message = CommandArg()):
    seed = int(time.time())
    random.seed(seed)
    minmum = random.randint(1, 50)
    maxnum = random.randint(minmum, 100)
    random_cache["start_time"] = time.time()
    target_number = random.randint(minmum, maxnum)
    # 计算最大猜测次数和超时时间
    # 将生成的随机数保存到缓存中s
    max_guess_count: int = int((maxnum - minmum) / 14) + 4
    timeout = int((maxnum - minmum) / 4) + 35 + random.randint(3, 25)
    random_cache["seed"] = seed
    random_cache["target"] = target_number
    random_cache["start_time"] = time.time()
    random_cache["timeout"] = timeout
    random_cache["guess_count"] = 0  # 初始化猜测次数计数器
    random_cache["max_guess_count"] = max_guess_count

    # 提示玩家开始猜数字
    await num.reject(MessageSegment.text(f"{timeout}秒内{max_guess_count}次机会从{minmum}~{maxnum}猜个数:"))


@num.handle()
async def num_handle_for(event: MessageEvent):
    random_cache["guess_count"] += 1
    now_time = time.time()
    # 从缓存中读取数据
    target_number = random_cache.get("target")
    guess_count = random_cache["guess_count"]
    max_guess_count = random_cache["max_guess_count"]
    start_time = random_cache["start_time"]
    timeout = random_cache["timeout"]

    time_consume = int(now_time - start_time)

    # 提取玩家输入的猜测
    message = event.get_message()
    user_guess = message.extract_plain_text()

    # 检查玩家输入是否为数字
    if not user_guess.isdigit():
        if user_guess in ("退出", "退出游戏", "stop"):
            random_cache.clear()
            await num.finish(MessageSegment.text("已退出游戏"))
        await num.reject()
        return
    user_guess = int(user_guess)

    if time_consume < timeout:
        # 比较玩家的猜测与目标数字,猜中后通知玩家
        if user_guess == target_number:
            await num.finish(
                MessageSegment.reply(event.message_id) + MessageSegment.text(
                    f"用时{time_consume}秒猜了{guess_count}次就猜对了") + MessageSegment.face(99))

        elif user_guess > target_number:
            await num.send(MessageSegment.text("大了"))
            if random_cache["guess_count"] >= random_cache["max_guess_count"]:
                await num.finish(MessageSegment.text(f"笨蛋！猜了{max_guess_count}次都没猜对") + MessageSegment.face(27))
            await num.reject()
        else:
            await num.send(MessageSegment.text("小了"))
            if random_cache["guess_count"] >= random_cache["max_guess_count"]:
                await num.finish(MessageSegment.text(f"主人好菜，{max_guess_count}次都没猜对") + MessageSegment.face(9))
            await num.reject()
    else:
        await num.finish(MessageSegment.text(f"游戏都超时啦！别猜了") + MessageSegment.face(64))
